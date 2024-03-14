# dashcam
A simple DashCam in Python

This is probably *NOT* the cheapest way to get a DashCam for your vehicle, but it is a lot more fun that popping into your local auto parts store.  I created it with the following components in mind:

* Raspberry Pi (probably a zero) with the hardwired camera.
* Serial GPS receiver
* External storage device
* OpenCV for image processing

The GPS module gets around the issue that the Pi has no built-in timekeeping, and as a bonus we can track where we are.
