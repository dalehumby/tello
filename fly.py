"""
Simple Tello drone flyer

Drone axes:
TODO Need to confirm signs, but the XYZ axes are corrent. Seems like right hand co-ordinate system
- X Forward+/Aft-
- Y Left+/Right-
- Z Up+/Down-

Camera axes:
- The video height (Y axis) is along the drone vertical, Z axis
- The video width (X axis) is along the drone horizontal, Y axis

IMU axes:

MVO axes:

"""

import sys
import traceback
import tellopy
import av
import cv2.cv2 as cv2  # for avoidance of pylint error
import numpy as np
import time
from aruco import Tracker
from simple_pid import PID

SPEED = 20
MAX_SPEED = 40
CAMERA_HEIGHT, CAMERA_WIDTH = 720, 960
CAMERA_VFOV = 43
CAMERA_HFOV = 60
CAMERA_HORIZON = 185

flight_data = None
log_data = None

def draw_text(image, text, row):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_size = 24
    font_color = (255,255,255)
    left_mergin = 10
    if row < 0:
        pos =  (left_mergin, CAMERA_HEIGHT + font_size * row + 1)
    else:
        pos =  (left_mergin, font_size * (row + 1))
    cv2.putText(image, text, pos, font, font_scale, font_color, 1, cv2.LINE_AA)


def draw_hud(image, autopilot_on):
    """Draw heads up display (HUD) on the image."""
    # Draw horizontal and vertical line in middle of frame
    #color = (191, 201, 202)
    #x, y = int(CAMERA_WIDTH/2), int(CAMERA_HEIGHT/2)
    #cv2.line(image, (0, y), (CAMERA_WIDTH, y), color, 1, cv2.LINE_AA)
    #cv2.line(image, (x, 0), (x, CAMERA_HEIGHT), color, 1, cv2.LINE_AA)
    image = draw_horizon(image)

    # Flight dynamics
    if flight_data:
        draw_text(image, str(flight_data), 0)
    if log_data:
        draw_text(image, 'MVO: ' + str(log_data.mvo), -3)
        draw_text(image, ('IMU: ' + str(log_data.imu))[0:52], -2)
        draw_text(image, '     ' + ('IMU: ' + str(log_data.imu))[52:], -1)

    draw_text(image, 'Autopilot: ' + str(autopilot_on), 1)

    return image


def draw_horizon(image):
    """Draw artificial horizon on the heads up display.
    Looks something like ---- o ----
    TODO make the horizon pitch and roll as drone moves."""
    color = (191, 201, 202)
    cntr_x, cntr_y = int(CAMERA_WIDTH/2), CAMERA_HORIZON
    length = 100
    cv2.circle(image, (cntr_x, cntr_y), 5, color, 1, cv2.LINE_AA)
    cv2.line(image, (cntr_x-10, cntr_y), (cntr_x-10-length, cntr_y), color, 1, cv2.LINE_AA)
    cv2.line(image, (cntr_x+10, cntr_y), (cntr_x+10+length, cntr_y), color, 1, cv2.LINE_AA)
    return image


def draw_reticle(image, reticle):
    """Draw the reticle on the image."""
    color = (191, 201, 202)
    length = 25
    x, y = reticle
    cv2.line(image, (x-length, y), (x+length, y), color, 1, cv2.LINE_AA)
    cv2.line(image, (x, y-length), (x, y+length), color, 1, cv2.LINE_AA)
    return image


def calc_gluideslope(angle):
    """Calculate the (x,y) position of the reticle given a glide slope in degrees.
    Negative means down."""
    pixels_per_degree = CAMERA_HEIGHT / CAMERA_VFOV
    x = round(CAMERA_WIDTH / 2)
    y = round(CAMERA_HORIZON - angle * pixels_per_degree)
    return (x, y)


def flight_data_handler(event, sender, data, **args):
    global flight_data, log_data
    drone = sender
    if event is drone.EVENT_FLIGHT_DATA:
        flight_data = str(data)
    elif event is drone.EVENT_LOG_DATA:
        log_data = data


def fly_with_keyboard(drone, key):
    """Command the drone from the keyboard."""
    if key == ord('t'):
        drone.takeoff()
    elif key == ord('l') or key == 32:
        # TODO space (key 32) should be emergency stop
        drone.land()
    elif key == ord('s'):
        drone.backward(SPEED)
    elif key == ord('w'):
        drone.forward(SPEED/2)
    elif key == ord('a'):
        drone.left(SPEED)
    elif key == ord('d'):
        drone.right(SPEED)
    elif key == ord('q'):
        drone.counter_clockwise(SPEED)
    elif key == ord('e'):
        drone.clockwise(SPEED)
    elif key == ord('c'):
        drone.up(SPEED)
    elif key == ord('z'):
        drone.down(SPEED)
    elif key == ord('x'):
        # Make drone hover
        drone.left(0)
        drone.right(0)
        drone.up(0)
        drone.down(0)
        drone.counter_clockwise(0)
        drone.clockwise(0)
        drone.forward(0)
        drone.backward(0)
    elif key != 255:
        print('Unknown key pressed:', key)


def quat2euler(w, x, y, z):
    """
    This is a modified version of this:
    https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
    """
    from math import atan2, pi, asin
    ysqr = y * y

    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + ysqr)
    X = atan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    Y = asin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (ysqr + z * z)
    Z = atan2(t3, t4)

    X *= 180/pi
    Y *= 180/pi
    Z *= 180/pi

    return (X, Y, Z,)



def main():
    drone = tellopy.Tello()
    tracker = Tracker()
    control_y = PID(-0.08, -0.007, -0.003, setpoint=0)
    control_z = PID(-0.15, -0.01, -0.005, setpoint=0)
    control_yaw = PID(-0.08, -0.007, -0.003, setpoint=0)
    control_y.sample_time = 1/60
    control_z.sample_time = 1/60
    control_yaw.sample_time = 1/60
    control_y.output_limits = (-MAX_SPEED, MAX_SPEED)
    control_z.output_limits = (-MAX_SPEED, MAX_SPEED)
    control_yaw.output_limits = (-MAX_SPEED, MAX_SPEED)
    reticle = calc_gluideslope(-5)

    try:
        drone.subscribe(drone.EVENT_FLIGHT_DATA, flight_data_handler)
        drone.subscribe(drone.EVENT_LOG_DATA, flight_data_handler)

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

        # Start without the autopilot
        autopilot_on = False
        control_y.auto_mode = False
        control_z.auto_mode = False
        control_yaw.auto_mode = False

        frame_skip = 300  # Skip first frames
        while True:
            for frame in container.decode(video=0):
                # If transforms are taking too long then start skipping frames
                if frame_skip > 0:
                    frame_skip -= 1
                    continue
                start_time = time.time()
                image = cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)

                # Key presses give the drone a speed, and not a distance to move. Press x to stop all movement
                key = cv2.waitKey(1) & 0xFF
                fly_with_keyboard(drone, key)

                # Toggle autopilot
                if key == ord('p'):
                    autopilot_on = not autopilot_on
                    if autopilot_on:
                        #control_y.auto_mode = True
                        control_z.auto_mode = True
                        control_yaw.auto_mode = True
                    else:
                        #control_y.auto_mode = False
                        control_z.auto_mode = False
                        control_yaw.auto_mode = False

                tracker.update(image)
                image = tracker.draw_markers(image)
                image = draw_reticle(image, reticle)
                error_yaw, error_z, error_y = tracker.calc_error(2, reticle)

                #print('Errors:', error_yaw, error_z, error_y)

                v_y = control_y(error_y)
                v_z = control_z(error_z)
                v_yaw = control_yaw(error_yaw)
                #print('error y', error_y, 'v_y', v_y, 'PID', control_y.components)
                #print('error z', error_z, 'v_z', v_z, 'PID', control_z.components)
                #print('error yaw', error_y, 'v_yaw', v_yaw, 'PID', control_yaw.components)

                #print(log_data.imu)
                #print(type(log_data.imu))
                imu = log_data.imu
                #print(quat2euler(imu.q0, imu.q1, imu.q2, imu.q3))  # roll, pitch, yaw

                tracker.draw_axes(image)

                try:
                    if tracker.distances[0] < 1000:
                        control_y.auto_mode = True
                    else:
                        control_y.auto_mode = False
                except KeyError:
                    pass

                if autopilot_on:
                    if v_z is None:
                        pass
                    elif v_z > 0:
                        drone.up(v_z)
                    else:
                        drone.down(abs(v_z))

                    if v_y is None:
                        pass
                    elif v_y > 0:
                        drone.right(v_y)
                    else:
                        drone.left(abs(v_y))

                    if v_yaw is None:
                        pass
                    elif v_yaw > 0:
                        drone.clockwise(v_yaw)
                    else:
                        drone.counter_clockwise(abs(v_yaw))


                # Display an image with edge detection. Make smaller so can fit on screen with the HUD
                #img = cv2.resize(image, (300, 225))
                #cv2.imshow('Canny', cv2.Canny(img, 100, 200))

                # Display full image with HUD
                image = draw_hud(image, autopilot_on)
                cv2.imshow('Drone', image)

                # Determine if need to skip any frames
                if frame.time_base < 1.0/60:
                    time_base = 1.0/60
                else:
                    time_base = frame.time_base
                frame_skip = int((time.time() - start_time)/time_base)


    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print(ex)
    finally:
        drone.quit()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
