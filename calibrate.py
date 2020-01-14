"""
Connect to the drone and calibrate the camera
"""

import time
import tellopy
import av
import cv2.cv2 as cv2  # for avoidance of pylint error
from cv2 import aruco
import numpy as np

aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
board = aruco.CharucoBoard_create(7, 5, 1, .8, aruco_dict)

def make_chessboard():
    """Make a "chess" aruco board, and save to file for printing."""
    imboard = board.draw((2000, 2000))
    cv2.imwrite('chessboard.tiff', imboard)


def calibrate_camera(allCorners,allIds,imsize):
    """Calibrates the camera using the dected corners."""
    print("CAMERA CALIBRATION")

    cameraMatrixInit = np.array([[ 1000.,    0., imsize[0]/2.],
                                 [    0., 1000., imsize[1]/2.],
                                 [    0.,    0.,           1.]])

    distCoeffsInit = np.zeros((5,1))
    flags = (cv2.CALIB_USE_INTRINSIC_GUESS + cv2.CALIB_RATIONAL_MODEL + cv2.CALIB_FIX_ASPECT_RATIO)

    (ret, camera_matrix, distortion_coefficients0,
     rotation_vectors, translation_vectors,
     stdDeviationsIntrinsics, stdDeviationsExtrinsics,
     perViewErrors) = cv2.aruco.calibrateCameraCharucoExtended(
                      charucoCorners=allCorners,
                      charucoIds=allIds,
                      board=board,
                      imageSize=imsize,
                      cameraMatrix=cameraMatrixInit,
                      distCoeffs=distCoeffsInit,
                      flags=flags,
                      criteria=(cv2.TERM_CRITERIA_EPS & cv2.TERM_CRITERIA_COUNT, 10000, 1e-9))

    return ret, camera_matrix, distortion_coefficients0, rotation_vectors, translation_vectors


def main():
    drone = tellopy.Tello()
    drone.connect()
    drone.wait_for_connection(60.0)

    retry = 3
    container = None
    while container is None and 0 < retry:
        retry -= 1
        try:
            container = av.open(drone.get_video_stream())
        except av.AVError as ave:
            print(ave)
            print('retry...')

    allCorners = []
    allIds = []
    decimator = 0
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.00001)  # Subpixel corner detection criteria

    capture_images = True
    frame_skip = 300  # Skip first frames
    while capture_images:
        for frame in container.decode(video=0):
            # If transforms are taking too long then start skipping frames
            if frame_skip > 0:
                frame_skip -= 1
                continue
            start_time = time.time()
            image = cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_BGR2GRAY)
            corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(image, aruco_dict)

            if len(corners)>0:
                # SUB PIXEL DETECTION
                for corner in corners:
                    cv2.cornerSubPix(image, corner,
                                     winSize = (3,3),
                                     zeroZone = (-1,-1),
                                     criteria = criteria)
                res2 = cv2.aruco.interpolateCornersCharuco(corners, ids, image, board)
                if res2[1] is not None and res2[2] is not None and len(res2[1]) > 3 and decimator%1 == 0:
                    allCorners.append(res2[1])
                    allIds.append(res2[2])

            decimator+=1


            # Key presses give the drone a speed, and not a distance to move. Press x to stop all movement
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                capture_images = False
                break

            # Display image
            cv2.imshow('Drone', image)

            # Determine if need to skip any frames
            if frame.time_base < 1.0/60:
                time_base = 1.0/60
            else:
                time_base = frame.time_base
            frame_skip = int((time.time() - start_time)/time_base)
            frame_skip += 30
            print('.',)

    # Done with calibration
    drone.quit()
    cv2.destroyAllWindows()
    imsize = image.shape
    ret, mtx, dist, rvecs, tvecs = calibrate_camera(allCorners, allIds, imsize)
    print('ret', ret)
    print('mtx', mtx)
    print('dist', dist)
    print('rvect', rvecs)
    print('tvect', tvecs)


if __name__ == '__main__':
    main()
