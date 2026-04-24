import cv2
import time
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from subsystem.structure import Subsystem
from models.FramePacket import FramePacket
from utility.loader import load_config

logger = logging.getLogger(__name__)

# Attempt pylon import once at module level — no hard dependency
try:
    from pypylon import pylon
    PYLON_AVAILABLE = True
except ImportError:
    PYLON_AVAILABLE = False
    logger.info("pypylon not found — Pylon backend unavailable, falling back to OpenCV")


class VisionSubsystem(Subsystem):
    def __init__(self, bus):
        super().__init__(bus)
        self.config = load_config()
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="vision_grab")

        vision_cfg = self.config.get("vision", {})
        requested_backend = vision_cfg.get("backend", "opencv").lower()

        # Resolve effective backend: honour config request, but fall back if pylon missing
        if requested_backend == "pylon" and not PYLON_AVAILABLE:
            logger.warning("Config requested pylon backend but pypylon is not installed — falling back to OpenCV")
            requested_backend = "opencv"

        self._backend = requested_backend

        if self._backend == "pylon":
            self._cam = self._init_pylon(vision_cfg)
        else:
            self._cam = self._init_opencv(vision_cfg)

        logger.info("VisionSubsystem initialised with backend: %s", self._backend)

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------

    def _init_pylon(self, vision_cfg: dict):
        """Open a Basler camera via pylon, applying config overrides."""
        tlf = pylon.TlFactory.GetInstance()

        serial = vision_cfg.get("pylonSerial")
        if serial:
            device_info = pylon.CDeviceInfo()
            device_info.SetSerialNumber(serial)
            device = tlf.CreateDevice(device_info)
        else:
            # First available camera
            device = tlf.CreateFirstDevice()

        cam = pylon.InstantCamera(device)
        cam.Open()

        # Pixel format — Mono8 is fastest for monochrome at high fps
        pixel_format = vision_cfg.get("pylonPixelFormat", "Mono8")
        cam.PixelFormat.SetValue(pixel_format)

        # Optional ROI — reduces bandwidth dramatically at high fps
        if "pylonWidth" in vision_cfg:
            cam.Width.SetValue(vision_cfg["pylonWidth"])
        if "pylonHeight" in vision_cfg:
            cam.Height.SetValue(vision_cfg["pylonHeight"])
        if "pylonOffsetX" in vision_cfg:
            cam.OffsetX.SetValue(vision_cfg["pylonOffsetX"])
        if "pylonOffsetY" in vision_cfg:
            cam.OffsetY.SetValue(vision_cfg["pylonOffsetY"])

        # Exposure
        if "pylonExposureUs" in vision_cfg:
            cam.ExposureTime.SetValue(vision_cfg["pylonExposureUs"])

        # Grab strategy: LatestImageOnly drops stale frames under load,
        # keeping the pipeline at the front of the stream.
        cam.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

        logger.info(
            "Pylon camera opened: %s  |  %dx%d  |  %s",
            cam.GetDeviceInfo().GetSerialNumber(),
            cam.Width.GetValue(),
            cam.Height.GetValue(),
            pixel_format,
        )
        return cam

    def _init_opencv(self, vision_cfg: dict) -> cv2.VideoCapture:
        camera_id = vision_cfg.get("cameraID", 0)
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            raise RuntimeError(f"OpenCV could not open camera ID {camera_id}")

        if "opencvWidth" in vision_cfg:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, vision_cfg["opencvWidth"])
        if "opencvHeight" in vision_cfg:
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, vision_cfg["opencvHeight"])
        if "opencvFps" in vision_cfg:
            cap.set(cv2.CAP_PROP_FPS, vision_cfg["opencvFps"])

        logger.info("OpenCV camera opened: ID %s", camera_id)
        return cap

    # ------------------------------------------------------------------
    # Blocking grab functions — run in thread pool to stay non-blocking
    # ------------------------------------------------------------------

    def _grab_pylon(self):
        """
        Blocking grab from Basler camera.
        Returns (frame_np, t_capture, hw_timestamp_ns) or (None, None, None) on miss.
        """
        result = self._cam.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
        try:
            if not result.GrabSucceeded():
                logger.debug("Pylon grab failed: %s", result.ErrorDescription)
                return None, None, None

            t_capture = time.monotonic()
            hw_timestamp_ns = result.TimeStamp  # camera hardware timestamp (ns)
            frame = result.GetArray()           # numpy array, zero-copy view
            frame = frame.copy()                # own the data before result release
            return frame, t_capture, hw_timestamp_ns
        finally:
            result.Release()

    def _grab_opencv(self):
        """
        Blocking grab from OpenCV camera.
        Returns (frame_np, t_capture, None) or (None, None, None) on miss.
        """
        ret, frame = self._cam.read()
        if not ret:
            return None, None, None
        return frame, time.monotonic(), None

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    async def start(self):
        loop = asyncio.get_running_loop()
        grab_fn = self._grab_pylon if self._backend == "pylon" else self._grab_opencv

        try:
            while True:
                frame, t_capture, hw_timestamp_ns = await loop.run_in_executor(
                    self._executor, grab_fn
                )

                if frame is None:
                    await asyncio.sleep(0.001)
                    continue

                packet = FramePacket(
                    frame=frame,
                    timestamp=t_capture,
                    hw_timestamp_ns=hw_timestamp_ns,  # None for OpenCV path
                )

                await self.bus.publish("frame", packet)

        finally:
            self._shutdown()

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def _shutdown(self):
        logger.info("VisionSubsystem shutting down (%s)", self._backend)
        try:
            if self._backend == "pylon":
                if self._cam.IsGrabbing():
                    self._cam.StopGrabbing()
                self._cam.Close()
            else:
                self._cam.release()
        except Exception as exc:
            logger.warning("Error during camera shutdown: %s", exc)
        self._executor.shutdown(wait=False)