# Autopilot for Tello drone

This project was started from the question "_Could_ you use a Tello drone as an indoor surveillance drone?" I'm using that goal as a rough purpose, but this project is mostly about having fun building an autopilot for a drone, and learn a bit more about PID algorithms, kalman filters, use CV2 for image processing, numpy, how to locate and navigate a drone, etc.

At this stage I'm commiting my work to GitHub so that I have a remote repo. I might neaten up the project later so others can replicate this.

## Active development
- [x] Send commands to the drone, receive video using [TelloPy](https://github.com/hanyazou/TelloPy)
- [x] Get the drone to fly up/down and translate left/right, tracking a coloured marker using OpenCV and a PID algorithm
- [ ] Track an aruco marker
- [ ] Home in on a specific aruco marker, fly a descent profile, measure distance to marker, land when ligned up with marker

History of my progress in [Journal](journal.md)
