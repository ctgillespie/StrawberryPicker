# Strawberry Picker/Mover
## Introduction
The impetus behind this project was to develop a small prototype for a strawberry moving robot for use in vertical farming applications. Vertical farms typically have plants growing out of a cylinder to save on space. However, the spacing between plants in the cylinder is important to ensure that each plant has the room it needs to grow. Moving these plants is a task that can easily be automated with the use of a pick-and-place machine designed to operate on the cylinder. <br /> <br />
This project serves as a proof-of-concept for such a system. It uses a foam roller with push-pins as a representative model of the vertical farm and strawberries. The roller is rotated by a stepper motor and the pins are manipulated using a robotic arm with a gripper mounted to it. The arm uses one stepper motor for its base, a modified servo for its elbow, and an un-modified servo for its wrist and claw.
## Hardware Design
## Motor Driver
## Image Parsing
The functionality of the robot was expanded beyond the simple pick-and-place system described in the introduction into something that can “draw” pictures by placing the pins in certain places on the roller. In order to load these images onto the controller, the pictures are first drawn in *Inkscape*. In order to draw a picture in a way that the program can recognize, the circle tool is used. A red circle (or any color other than black) indicates a starting location for a pin and a black circle indicates a final location. The circles may be created using any size. An example image is shown below. <br />
![alt text](https://github.com/ctgillespie/StrawberryPicker/blob/main/Photos/SmileDrawing.PNG?raw=true "Smile Example")
Because each circle represents an initial or final pin position, the number of red (start) positions must equal the number of black (end) positions. Once the drawing is complete, it is exported as an xml file so that the locations of each start and end positions can be read in. The corresponding xml file for the example image above is included in the files attached with this report above.
## Motor Command Generation
## Cooperative Multitasking
![alt text](https://github.com/ctgillespie/StrawberryPicker/blob/main/Photos/TaskDiagram.PNG?raw=true "Task Diagram")
## Demonstration
