# cv-notifier <img src="https://cdn-icons-png.flaticon.com/512/1527/1527254.png" height="5%" width="5%" align="left"/>

![Build Status](https://github.com/circa10a/cv-notifier/workflows/deploy/badge.svg)
![GitHub tag (latest semver)](https://img.shields.io/github/v/tag/circa10a/cv-notifier?style=plastic)

Easily detect objects using computer vision ([YOLOv8](https://github.com/ultralytics/ultralytics)) and call configurable webhooks. Built for easy object detection on x86/arm64 machines.

![alt text](https://media.tenor.com/rEfUBOuVFZcAAAAC/stalker-peeping-tom.gif)

* [About](#about)
* [Usage](#usage)
  * [System requirements](#system-requirements)
  * [Local](#local)
  * [Docker](#docker)
* [Configuration](#configuration)
  * [Variable substituiton](#variable-substituiton)

## About

I primarily built this because I wanted to be able to notify my cat that there are birds/squirrels on my patio since he often yells at me to summon said birds/squirrels all of the time. I thought an application such as this existed already. All I wanted was to be able to call webhooks when a certain object is detected on a video stream, but yet, here we are because it didn't exist.

I'm using this with an RTSP stream via [this cheap ip camera](https://www.amazon.com/Tapo-security-indoor-pet-camera/dp/B0866S3D82) along with [home assistant](https://www.home-assistant.io/) to play sounds on my Google Home speakers. Everything is hosted on a Raspberry Pi 4 via docker containers.

## Usage

`cv-notifier` is very configurable, thus requires a YAML or JSON configuration file at runtime. See [configuration](#configuration) for more details.

Here's what an example configuration file looks like:

```yaml
config:
  source: 'rtsp://$STREAM_USER:$STREAM_PASSWORD@192.168.1.101/stream1'
  schedule:
    startTime: '07:00'
    endTime: '18:00'
  webhooks:
    - url: http://localhost:8080?object_name=$object_name&object_confidence=$object_confidence
      notifyInterval: 900
      objects:
        - bird
        - cat
        - dog
      method: 'POST'
      headers:
        Content-Type: application/json
        Authorization: Bearer $API_TOKEN
      body: >
        {
          "someKey": "$object_name detected with confidence score of $object_confidence"
        }
```

### System requirements

* x86
  * 2 CPU's
  * 500M available RAM
* ARM (Raspberry Pi 4 recommended)
  * 3 CPU's
  * 500M available RAM

### Local

```console
python main.py --config ./sample.config.yaml
```

### Docker

Docker run:

> Variable substitution in the configuration is optional. This is to demonstrate capabilities.

```console
docker run --name cv-notifier \
    -e STREAM_USER=$USER \
    -e STREAM_PASSWORD=password \
    -e API_TOKEN='token' \
    -v $PWD/sample.config.yaml:/opt/cv-notifier/config.yaml \
    -v /etc/localtime:/etc/localtime:ro \
    circa10a/cv-notifier
```

Docker Compose:

```yaml
version: '3'

services:
  cv-notifier:
    container_name: cv-notifier
    restart: always
    image: circa10a/cv-notifier
    env_file: .env
    volumes:
      - ./sample.config.yaml:/opt/cv-notifier/config.yaml
      - /etc/localtime:/etc/localtime:ro
```

## Configuration

`cv-notifier` supports many different configuration options. See [usage](#usage)

|                                     |                                                                      |           |                    |                                |
|-------------------------------------|----------------------------------------------------------------------|-----------|--------------------|--------------------------------|
| Key                                 | Description                                                          | Required  | Default            | Supports environment variables |
| `config.source`                     | Source of video stream such as `RTSP`, `RTMP`, `HTTP`                | `True`    | `None`             |  ✅                            |
| `config.model`                      | What pre-trained model to use                                        | `False`   | `yolov8s.pt`       |  ❌                            |
| `config.confidence`                 | Score filter to only show detected objects with confidence above this| `False`   | `0.50` (50%)       |  ❌                            |
| `config.loglevel`                   | Level of logging. `info`, `debug`, `warning`                         | `False`   | `info`             |  ❌                            |
| `config.schedule.startTime`         | Time to start detecting objects/send notifications in 24 hour format | `False`   | `None`             |  ❌                            |
| `config.schedule.endTime`           | Time to stop detecting objects/send notifications in 24 hour format  | `False`   | `None`             |  ❌                            |
| `config.webhooks`                   | List of webhook configurations to be notified                        | `False`   | `None`             |  N/A                           |
| `config.webhooks[0].url`            | HTTP endpoint to send request to when object is detected             | `True`    | `None`             |  ✅                            |
| `config.webhooks[0].notifyInterval` | In seconds, frequency at which to send notifications                 | `False`   | `0`                |  ❌                            |
| `config.webhooks[0].objects`        | [List][COCO list] of things to detect and notify if seen             | `True`    | `[]`               |  ❌                            |
| `config.webhooks[0].method`         | HTTP method to send in request                                       | `False`   | `POST`             |  ❌                            |
| `config.webhooks[0].headers`        | Map of HTTP headers to send in request                               | `False`   | `None`             |  ✅                            |
| `config.webhooks[0].body`           | HTTP body to send in request                                         | `False`   | `None`             |  ✅                            |
| `config.webhooks[0].timeout`        | HTTP request timeout in seconds                                      | `False`   | `5`                |  ❌                            |

### Variable substituiton

Configuration fields that often require sensitive data do support environment variable subtsition in the form of `$variable` within the configuration values. The `url`, `body`, and `headers within a webhook configuration supports some additional data around the object detected. This information can be used to customize request payloads like the example mentioned above in [configuration](#configuration).

* `object_name` - The name of the object detected that was specified in the `objects` list
* `object_confidence` - The confidence score from the model of the object detected

<!-- References -->
[COCO list]: https://gist.github.com/AruniRC/7b3dadd004da04c80198557db5da4bda
