import cv2.cv2 as cv2
from math import radians, tanh, pi
from calibresults import camera_matrix, dist_coeff

CAMERA_HEIGHT, CAMERA_WIDTH = 720, 960
CAMERA_VFOV = 43
CAMERA_HFOV = 60
MARKER_HEIGHT, MARKER_WIDTH = 100, 100

class Tracker:
    """Aruco tracking."""
    def __init__(self):
        self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        self.parameters =  cv2.aruco.DetectorParameters_create()
        self.parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
        self.markers = {}
        self.centres = {}
        self.distances = {}
        self._corners = None
        self._marker_ids = None

    @staticmethod
    def _calc_distance(corners):
        """Calculate the distance to a marker.
        Assumes target is perpendicular to camera axis, and far enough away that right-angle geometry is accurate enough."""
        angle = radians(CAMERA_HFOV) / CAMERA_WIDTH * (corners[1][0] - corners[0][0])
        return round(MARKER_WIDTH / tanh(angle))

    def update(self, image):
        """Given an image, detect all markers in the image."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self._corners, self._marker_ids, rejected_points = cv2.aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)
        self.markers = {}
        self.centres = {}
        self.distances = {}
        if self._marker_ids is None:
            return
        for i in range(len(self._marker_ids)):
            marker_id = self._marker_ids[i][0]
            c = self._corners[i][0]
            self.centres[marker_id] = (round(c[:, 0].mean()), round(c[:, 1].mean()))
            c = [ tuple(xy) for xy in c.tolist() ]
            self.markers[marker_id] = c
            self.distances[marker_id] = self._calc_distance(c)

    def draw_markers(self, image):
        """Draw the detected markers on an image. Assumed to be the same image that `update` was run on."""
        for marker_id, d in self.distances.items():
            x = int(self.markers[marker_id][1][0]) + 5
            y = int(self.markers[marker_id][1][1]) + 5
            s = 'd=%s' % d
            cv2.putText(image, s, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1, cv2.LINE_AA)
        return cv2.aruco.drawDetectedMarkers(image, self._corners, self._marker_ids)

    def draw_axes(self, image):
        """Draw the xyz markers on the image."""
        if self._marker_ids is None:
            return image
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(self._corners, MARKER_HEIGHT , camera_matrix, dist_coeff)
        print('rvecs', (rvecs*180/pi).round(), 'tvecs', tvecs.round())
        image = cv2.aruco.drawDetectedMarkers(image, self._corners, self._marker_ids)
        for i in range(len(tvecs)):
            image = cv2.aruco.drawAxis(image, camera_matrix, dist_coeff, rvecs[i], tvecs[i], MARKER_HEIGHT)
        return image

    def calc_error(self, marker_id, reticle):
        """Find the delta between the centre of an aruco marker with id `marker_id`, and given (x,y) coordinate.
        Error is in same units as marker width (millimeters, in my case)
        If error_x > 0 then the centre of the marker is to the right of x
        If error_y > 0 then the centre of the marker is above y
        Recall that for images (0,0) is the top left corner.
        """
        if marker_id not in self.centres:
            return 0, 0, 0
        x, y = reticle
        error_x_px = self.centres[marker_id][0] - x
        error_y_px = y - self.centres[marker_id][1]
        c = self.markers[marker_id]
        width_px = c[1][0] - c[0][0]
        height_px = c[2][1] - c[1][1]
        error_x = MARKER_WIDTH / width_px * error_x_px
        error_y = MARKER_HEIGHT / height_px * error_y_px
        angle = (c[3][1] - c[0][1]) - (c[2][1] - c[1][1])  # Not really the angle, just proportional to the angle. TODO get correct angle
        angle *= 10  # Fudge factor
        return error_x, error_y, angle


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
        if marker_id in tracker.centres:
            cv2.line(image, reticle, tracker.centres[marker_id], color, 1, cv2.LINE_AA)

        print(tracker.markers)
        print(tracker.calc_error(marker_id, reticle))

        cv2.imshow("Tracker", image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            exit()

if __name__ == '__main__':
    main()

