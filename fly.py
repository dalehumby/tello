"""
Simple Tello drone flyer

Based off https://github.com/hanyazou/TelloPy/blob/develop-0.7.0/tellopy/examples/video_effect.py
"""
import sys
import traceback
import tellopy
import av
import cv2.cv2 as cv2  # for avoidance of pylint error
import numpy
import time

flight_data = None
log_data = None

def flight_data_handler(event, sender, data, **args):
    global flight_data, log_data
    drone = sender
    if event is drone.EVENT_FLIGHT_DATA:
        #print(data)
        flight_data = str(data)
    elif event is drone.EVENT_LOG_DATA:
        #print(str(data))
        log_data = str(data).split('|')
    elif event is drone.EVENT_TIME:
        time = data[0] << 8 | data[1]
        print('Time:', time)


def main():
    drone = tellopy.Tello()

    try:
        drone.subscribe(drone.EVENT_FLIGHT_DATA, flight_data_handler)
        drone.subscribe(drone.EVENT_LOG_DATA, flight_data_handler)
        drone.subscribe(drone.EVENT_TIME, flight_data_handler)

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

        # skip first 300 frames
        frame_skip = 300
        while True:
            for frame in container.decode(video=0):
                # If transforms are taking too long then start skipping frames
                if frame_skip > 0:
                    frame_skip -= 1
                    continue
                start_time = time.time()

                image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)

                # Display an image with edge detection. Make smaller so can fit on screen with the HUD
                #img = cv2.resize(image, (300, 225))
                #cv2.imshow('Canny', cv2.Canny(img, 100, 200))

                # Display full image with HUD
                cv2.putText(image, flight_data, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(image, log_data[0], (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(image, log_data[1], (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.imshow('Original', image)

                # Key presses give the drone a speed, and not a distance to move. Press x to stop all movement
                key = cv2.waitKey(1) & 0xFF
                if key == ord('t'):
                    drone.takeoff()
                elif key == ord('l'):
                    drone.land()
                elif key == ord('s'):
                    drone.backward(10)
                elif key == ord('w'):
                    drone.forward(10)
                elif key == ord('a'):
                    drone.left(10)
                elif key == ord('d'):
                    drone.right(10)
                elif key == ord('q'):
                    drone.counter_clockwise(20)
                elif key == ord('e'):
                    drone.clockwise(20)
                elif key == ord('c'):
                    drone.up(10)
                elif key == ord('z'):
                    drone.down(10)
                elif key == ord('x'):
                    # z: Make drone hover
                    drone.left(0)
                    drone.right(0)
                    drone.up(0)
                    drone.down(0)
                    drone.counter_clockwise(0)
                    drone.clockwise(0)
                    drone.forward(0)
                    drone.backward(0)
                elif key != 255:
                    print(key)

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
