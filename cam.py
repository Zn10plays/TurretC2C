import cv2
import numpy as np
import math

# ==========================
# INSERT YOUR CALIBRATION
# ==========================
cam_data = np.load('./cam_data/web_cam.npz')

camera_matrix = cam_data['camera_matrix']
dist_coeffs = cam_data['dist_coeffs']


def pixel_to_angles(u, v, camera_matrix, dist_coeffs):
    """
    Convert pixel coordinate (u,v) to yaw and pitch (degrees)
    """

    # Convert to proper shape for OpenCV
    pts = np.array([[[u, v]]], dtype=np.float32)

    # Undistort to normalized camera coordinates
    undistorted = cv2.undistortPoints(
        pts,
        camera_matrix,
        dist_coeffs
    )

    # Extract normalized coordinates
    x = undistorted[0][0][0]
    y = undistorted[0][0][1]

    # Camera ray in 3D
    ray = np.array([x, y, 1.0])

    # Normalize
    ray = ray / np.linalg.norm(ray)

    # Compute yaw and pitch
    yaw = math.degrees(math.atan2(ray[0], ray[2]))
    pitch = math.degrees(math.atan2(-ray[1], ray[2]))

    return yaw, pitch


# ==========================
# READ CAMERA STREAM
# ==========================

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Example 2D point (replace with click or detection)
    u = 283.49422155
    v = 259.6999319

    print(frame.shape)

    yaw, pitch = pixel_to_angles(u, v, camera_matrix, dist_coeffs)

    cv2.putText(frame, f"Yaw: {yaw:.2f} deg",
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 255, 0), 2)

    cv2.putText(frame, f"Pitch: {pitch:.2f} deg",
                (20, 80), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 255, 0), 2)

    cv2.circle(frame, (int(u), int(v)), 6, (0, 0, 255), -1)

    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
