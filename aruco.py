import cv2.cv2 as cv2
from math import radians, tanh

CAMERA_HEIGHT, CAMERA_WIDTH = 720, 960
CAMERA_VFOV = 43
CAMERA_HFOV = 60
MARKER_HEIGHT, MARKER_WIDTH = 100, 100

class Tracker:
    """Aruco tracking."""
    def __init__(self):
        self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        self.parameters =  cv2.aruco.DetectorParameters_create()
        self.markers = {}
        self.means = {}
        self.distances = {}
        self._corners = None
        self._ids = None

    @staticmethod
    def _calc_distance(corners):
        """Calculate the distance to a marker."""
        angle = radians(CAMERA_HFOV) / CAMERA_WIDTH * (corners[1][0] - corners[0][0])
        return round(MARKER_WIDTH / tanh(angle))

    def update(self, image):
        """Given an image, detect all markers in the image."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self._corners, self._ids, rejected_points = cv2.aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)
        self.markers = {}
        self.means = {}
        self.distances = {}
        if self._ids is None:
            return
        for i in range(len(self._ids)):
            id = self._ids[i][0]
            c = self._corners[i][0]
            self.means[id] = (round(c[:, 0].mean()), round(c[:, 1].mean()))
            c = [ tuple(xy) for xy in c.tolist() ]
            self.markers[id] = c
            self.distances[id] = self._calc_distance(c)

    def draw_markers(self, image):
        """Draw the detected markers on an image. Assumed to be the same image that `update` was run on."""
        return cv2.aruco.drawDetectedMarkers(image, self._corners, self._ids)

    def calc_error(self, id, reticle):
        """Find the delta between the centre of a aruco marker with id `id`, and given (x,y) coordinate.
        If error_x > 0 then the centre of the marker is to the right of x
        If error_y > 0 then the centre of the marker is above y
        Recall that for images (0,0) is the top left corner.
        """
        x, y = reticle
        if id not in self.means:
            return 0, 0
        error_x = self.means[id][0] - x
        error_y = y - self.means[id][1]
        return error_x, error_y


def main():
    """Demo how the tracker works."""
    import time
    from imutils.video import VideoStream

    vid_stream = VideoStream(src=0).start()
    time.sleep(1.0)  # Short delay to start getting data from camera
    tracker = Tracker()
    color = (255, 255, 255)
    reticle = (400, 400)
    marker_id = 2
    while True:
        image = vid_stream.read()
        tracker.update(image)
        image = tracker.draw_markers(image)
        if marker_id in tracker.means:
            cv2.line(image, reticle, tracker.means[marker_id], color, 1, cv2.LINE_AA)

        print(tracker.markers)
        print(tracker.calc_error(marker_id, reticle))

        cv2.imshow("Tracker", image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            exit()

if __name__ == '__main__':
    main()

