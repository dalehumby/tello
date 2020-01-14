# Journal

## Tue, 14 Jan
### Calibrated camera for pose estimation
Wrote `calibration.py` to calibrate the Tello camera so that I could use it for pose estimation - rotation and translation estimates - instead of my (hacky) solutions. Especially for knowing how far away from the target, and how far to yaw to square up the drone to the target.

Todo:
- fix the axes of the drone and target so that the current drone position + error = target.
- Using Right Handed coordinate system, Z+ is up, Y+ is left and X+ is forward. The closest I can find for an authorative source is Tello [mission pad pdf](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20Mission%20Pad%20User%20Guide.pdf). The IMU data from velocity, acceleration and MVO (down camera) seem to use different co-ordinate systems. Although I quite likely haven't understood it correctly. The TelloPy and Go code are not any help.

## Thur, 9 Jan
### Added distance measuring
Looks like horizontal field of view is 60 degrees, and vertical field of view is 43 degrees. Added distance measuring as part of `aruco.py`, so distances to all markers are calculated each time the positions are updated. At far distances (2-4 m) a 1 pixel change leads to 50-100 mm distance change, and so the distances jump around a lot. 
- Distances would need to be filtered to prevent this jitter if you wanted to keep station at a specific distance from the target.
- I should also use the vertical marker size and vertical field of view to clacualte distance, and perhaps average the distance calcs from the horizontal and vertical views.
- The algorithm assumes that there is no roll.

### Added a new artificial horizon (AH)
Made a nice AH that looks like ---- o ---- The line is static in the window as I dont anticipate the drone rolling and pitching much, but I might attempt to make a true AH.

I tried aligning the AH to the real horizon out my window, but it looks like the camera slowly moves the horizon up and down in the window. This could be a result of the drone changing its position while hovering, but also could be a camera stabilisation algorith in the drone. Although the forums seems to say there is no stabilisation in 4:3 aspect ratio.

### Added terget, reticle with gluide path
Getting ready for the drone to fly towards a target on a gluide path, like -5 degrees.

I did fly the drone towards the target, but as it got closer the tracking became progressivley more unstable. As the drone gets closer the size of the marker increases in the video frame and a relativley small real world distance leads to a large pixel displacement, and since the control algorithm is based on pixels not millimeters the drone goes a bit crazy.

- [ ] Now that I have distance to target, I can calculate vertical and horizontal errors in millimeters and feed that to the control algorithm.
- [ ] I still need to find out what units TelloPy uses. I have a hunch it is centimeters... I'll match those units.

## Tue, 7 Jan
Was very pleased with Sunday afternoons work. Drone aligned with a blue marker, first got it working in vertical (z axis), and then horizontally (y axis), spent most of the time writing my own PID implementation, but all the corner cases got me, so used [Simple PID](https://pypi.org/project/simple-pid/) instead. Lots of parameter tuning.

Monday evening did a quick-and-dirty implementation of [Aruco](https://mecaruco2.readthedocs.io/en/latest/notebooks_rst/Aruco/Aruco.html) tracking. At the moment it uses the first marker it sees and tracks that, focusing on the top left corder of the marker.

Next step is to generalise the [aruco.py] file, turn in to class, get mid point, get corners of specific marker or all markers. Only run the detection algorithm once for all markers.

Other todo's
- [x] The 'reticle' is the centre of the screen, but the drones camera faces about 10 degrees down, so this means the drone hovers higher than the target point. Need to put horizon marker on the horizon.
- [x] Might make a nice artificial horizon (AH) that moves with the roll and pitch of the drone. (Not that it should be rolling and pitching, but hey, it'll look cool.) I can already see some horrible corner cases with drawing the AH on the screen for high angles of attack and roll.
- [x] Implement a target (aim point) and reticle (cross hairs that the drone is trying to put on the target)
- [ ] Need to decide what the control loop should do when the target is not visible. At the moment the "error" between the target and reticle is assumed to be 0, but if the aruco detector fails to detect e.g. 1 in 5 frames the control algorithm will jitter, which is nasty. Probably need to make it handle `None`.


## Sun, 5 Jan 2020
Goals for next few days
- [x] Neaten up the fly.py code, put keyboard commands in to own function; use a handler for receiving video; 
- [x] Better heads up display that is extensible, because that is certainly going to become messy over course of the project
- [x] Implement basic PID control class
- [x] Use PID to get drone to align vertically with some marker (keep marker in middle of the frame)


## Sat, 4 Jan 2020
Wrote basic script that takes keyboard commands, sends them to drone, receives video footage and overlays a simple heads up display (HUD)

Based off of [TelloPy](https://github.com/hanyazou/TelloPy/blob/develop-0.7.0/tellopy/examples/video_effect.py)


## 1st week of Jan, 2020
Borrowed a Tello from Aaron. He bought it as an indoor survailance drone, sounded like a fun project, and since it's only gathering dust at his house he let me borrow it. I'll probably end up buying my own before too long.

Played with it using the iPhone all. Got good idea of its capability, and THB it'll suck as a survailance drone... much easier to just mount IP cameras through your house.
- Very short battery life (13 min), stripping off covers and propeller gaurds I got the weight from 86g down to 78g. This increased the battery life to 20 minutes. Not tooo bad, but also not great considering it takes about 90 minutes for a full charge
- Cannot charge while the drone is on. We initially thought we could modify the drone to use an induction charger, and get the drone to land on the induction plate. If the drone cannot be powered on while charging then we need a (complex) way of switching the power to the drone on and off using the flight control computer.
- Camera has narrow (86 degree) field of view. Adding fisheye or wide angle lens adds minimum of 8g weight, furhter reducing flight time.
- Punching / hard bumping the drone causes it to emergency stop.
- Closed doors are insurmountable obstacles :p
- Not good outdoors even in a light breeze the drone barely copes. 

This all said, it's still a fun project to get a drone to fly autonomously indoors. My project goals are:
- Can I get a computer to send flight commands to the drone?
- Learn the basics of image processing, to determin position in the room, navigate a predetermined course, obstacle avoidance
- Improve my knowledge of control algorithms like PID control and kalman filters

Stretch goals
- recognition of objects
- tracking of people, faces, control of the drone through hand/body/voice gestures
