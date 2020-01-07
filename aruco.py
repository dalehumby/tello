import time
import cv2.cv2 as cv2  # for avoidance of pylint error
from imutils.video import VideoStream

class Tracker:
    """Aruco tracking."""
    def __init__(self, target_x, target_y, id):
        self.target_x = int(target_x)
        self.target_y = int(target_y)
        self.id = id
        self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        self.parameters =  cv2.aruco.DetectorParameters_create()

    def track(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)
        image = cv2.aruco.drawDetectedMarkers(image, corners, ids)
        print(ids)
        if ids is not None and len(ids) > 0:
            c = corners[0][0]
            print(c[0])
            error_x = int(c[0][0] - self.target_x)
            error_y = int(self.target_y - c[0][1])
            print(error_x, error_y)
            return error_x, error_y, image
        else:
            return 0, 0, image


def main():
    vid_stream = VideoStream(src=0).start()

    # allow the camera or video file to warm up
    time.sleep(1.0)
    frame = vid_stream.read()
    aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
    parameters =  cv2.aruco.DetectorParameters_create()

    # keep looping until no more frames
    more_frames = True
    while more_frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        """
        id = 1  # Aruco ID to search for
        if ids and id in ids:
            i = np.where(ids == id)[0]
            print(ids)
            print(i)
            c = corners[i][0]
            mean = ([c[:, 0].mean()], [c[:, 1].mean()])
            print(mean)
        """
        if ids:
            c = corners[0][0]
            print(c[0])

        show(frame)
        frame = vid_stream.read()
        if frame is None:
            more_frames = False

    vid_stream.stop()
    cv2.destroyAllWindows()


def show(frame):
    """Show the frame to cv2 window"""
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        exit()


if __name__ == '__main__':
    main()

