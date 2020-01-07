# Journal

## Sun, 5 Jan 2020
### Goals for next few days
- [ ] Neaten up the fly.py code, put keyboard commands in to own function; use a handler for receiving video; 
- [ ] Better heads up display that is extensible, because that is certainly going to become messy over course of the project
- [ ] Implement basic PID control class
- [ ] Use PID to get drone to align vertically with some marker (keep marker in middle of the frame)


## Sat, 4 Jan 2020
Wrote basic script that takes keyboard commands, sends them to drone, receives video footage and overlays a simple heads up display (HUD)

Based off of [TelloPy](https://github.com/hanyazou/TelloPy/blob/develop-0.7.0/tellopy/examples/video_effect.py)


# 1st week of Jan, 2020
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
