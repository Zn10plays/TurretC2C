# Turret Command and Control

This project holds the RPI4B code for the turret project. The main goals for this repo is to do the following.

* Handle the targeting logic (detection and aiming)
* Control the low level actuators (motors)
* Provide a UI for logging and teleop

## Installation and Development
The following project is written in python but has a few parts that need to be configured prior to use and development.

#### Configuration  
For starters the **config/constants.yaml** and **cam_data/web_cam.npz** need to be configured. They store the robot constants, and camera parameters respectively. The camera parameters include the intrinsics and distortion coefficients. 

#### Installation
The package manager of choice here is **uv** and should be used wih it. Follow the example code to install and run.

```bash 
> git clone url
> cd TurretC2C
> uv sync # downloads packages

# and for running
> uv run main.py
```



## Methodology and Structure
This section describes the project design choices and structure of the code.

Key subtopic include:
* Motors and Controllers
* Vision
* Concurrency 
* subsystems

#### Motors and Controllers
There are two distinct motor controllers on the turret: 2 Moteus r4.11 and 1 Cytron 30A DC motor driver.

The **r4.11s are commanded over a CAN-FD** bus, and therefore we need a special adapter to communicate with the bus. Ideally we will have a the official Moteus pi3hat, with the official python or cpp lib. 
The **Cytron is commanded with PWM**, we use any open GPIO or the PWM capable pin on the hat. Node that the Cytron is a PWM driver, and the output frequency of the driver is equal to the input frequency of the driver, up to 20kHz.

The reason two different drivers are needed is because the turret uses 2 different types of motors. The r4.11s command a QDD powered by a BLDC, the Cytron commands a standard DC motor, specifically the one in the airsoft gearbox. 


#### Vision
The goal of vision is to provide accurate information about the scene, identify objects of interest, and provide spacial awareness.

There are 2 possible ways to accomplish this
* By a single camera
* By multiple cameras

A single digital camera simply cannot provide spacial awareness without the use of complex ML, or lidar assistance. But it can provide what is needed (target relative angles). So we use it for this project.

A stereo camera (multiple camera) setup is vastly superior however comes at the cost of higher compute and complexity. It can be implemented on pi however due to the lack of additional beneficial information obtained by this change, we leave it for future work.

**Camera Workflow**
The single camera workflow is very simple. 

Image is captured -> timestamped -> annotated -> converted to relative angles -> targets are streamed.


#### Concurrency
The project has a lot of moving parts that need to work concurrently, for example: The Camera and CAN-FD IO communication, the image procession, logging and telemetry, target selection and tracking. 

All of these tasks are blocking, and some are CPU intensive, therefore they must be parallelized in such a manner one does not effect another. 

For IO bound task like CAN-FD communication, it is handled directly in Asyncio and the process works on other tasks when we wait for a message to be sent and received. 