# cv-notifier <img src="https://cdn-icons-png.flaticon.com/512/1527/1527254.png" height="5%" width="5%" align="left"/>

Easily detect objects using computer vision ([YOLOv8](https://github.com/ultralytics/ultralytics)) and call configurable webhooks. Built for easy object detection on Raspberry Pi's.

![alt text](https://media.tenor.com/rEfUBOuVFZcAAAAC/stalker-peeping-tom.gif)

## About

I primarily built this because I wanted to be able to notify my cat that there are birds/squirrels on our back patio since he's a terrible predator and often yells at me to summon said birds/squirrels all of the time. I thought an application such as this existed already. I simply just wanted to be able to call webhooks when a certain object is detected on a video stream, yet, here we are because it didn't exist.

I'm using this with an RTSP stream via [this cheap ip camera](https://www.amazon.com/Tapo-security-indoor-pet-camera/dp/B0866S3D82) along with [home assistant](https://www.home-assistant.io/) to play sounds on my Google Home speakers.

## Usage
