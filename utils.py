import numpy as np

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
