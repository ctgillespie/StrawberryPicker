# Strawberry Picker/Mover
## Introduction
The impetus behind this project was to develop a small prototype for a strawberry moving robot for use in vertical farming applications. Vertical farms typically have plants growing out of a cylinder to save on space. However, the spacing between plants in the cylinder is important to ensure that each plant has the room it needs to grow. Moving these plants is a task that can easily be automated with the use of a pick-and-place machine designed to operate on the cylinder. <br /> <br />
This project serves as a proof-of-concept for such a system. It uses a foam roller with push-pins as a representative model of the vertical farm and strawberries. The roller is rotated by a stepper motor and the pins are manipulated using a robotic arm with a gripper mounted to it. The arm uses one stepper motor for its base, a modified servo for its elbow, and an un-modified servo for its wrist and claw.
## Hardware Design
## Motor Driver
In order to get the motors to run properly, there are several set-up steps that must be followed to configure the TMC4210 properly. Firstly, the enable pin *en_sd* must be set to 1 to enable interfacing with the motor driver. Next, the *V_MIN* and *V_MAX* parameters are set. These parameters are used to tell the motor below which speed it can stop and to put an upper bound on the velocity of the motor respectively. Next, *PULSE_DIV* and *RAMP_DIV* are used to set the clock pre-dividers. An image of the clock signal on the oscilloscope is shown below. <br />
![alt text](https://github.com/ctgillespie/StrawberryPicker/blob/main/Photos/ClockSignal.PNG?raw=true "Smile Example")
## Image Parsing
The functionality of the robot was expanded beyond the simple pick-and-place system described in the introduction into something that can “draw” pictures by placing the pins in certain places on the roller. In order to load these images onto the controller, the pictures are first drawn in *Inkscape*. In order to draw a picture in a way that the program can recognize, the circle tool is used. A red circle (or any color other than black) indicates a starting location for a pin and a black circle indicates a final location. The circles may be created using any size. An example image is shown below. <br />
![alt text](https://github.com/ctgillespie/StrawberryPicker/blob/main/Photos/SmileDrawing.PNG?raw=true "Smile Example")
Because each circle represents an initial or final pin position, the number of red (start) positions must equal the number of black (end) positions. Once the drawing is complete, it is exported as an xml file so that the locations of each start and end positions can be read in. The corresponding xml file for the example image above is included in the files attached with this report above.
## Motor Command Generation
The xml file is then read into the Jupyter file _GenerateMotorCommands_ which, as the name suggests, generates motor commands based on the xml of the image provided. Firstly, it parses through the xml file and creates StartPoint and EndPoint objects for each pin, including the position and placed state. Each object is added to a list that the code will use to build a path from. The buildPath function will pop a start location off of the list, then use a custom interpolation function to make intermediate X, Y, and Z points for the robot to follow. This interpolation function can be tuned to either speed up or slow down the operation of the robot. Next, the buildPath function will call the pick function which will add in the X, Y, and Z coordinates to open the grabber, move in horizontally, close the grabber, and move out horizontally. Then another genPath function is called to move from the pick location to the place location. The place function is then called to do the opposite of the pick function. This whole process repeats, adding X, Y, Z locations and a Grab flag to an ever growing array to describe the entire motion of the robot as it draws the image. Finally, once the buildPath function is done, a Newton-Raphson solver is applied to each time step to convert X, Y, Z into motor locations to each of the four motors, under the constraint that the grabber must always remain horizontal. These motor commands along with the grab flag (1 for closed, 0 for open) are plotted below.
![alt text](https://github.com/ctgillespie/StrawberryPicker/blob/main/Photos/MotorCommandGraph.PNG?raw=true "Motor Commands")
![alt text](https://github.com/ctgillespie/StrawberryPicker/blob/main/Photos/GrabGraph.PNG?raw=true "Grab Commands")
## Cooperative Multitasking
At the highest level, the code onboard the Nucleo board runs cooperatively. After the initial set-up of writing the parameters to the motor board (as described in the Motor Driver section above), the multi-tasking part of the operation begins. There are two main tasks that run simultaneously. One reads the motor commands and the other writes to the motors. Since the Nucleo board has limited RAM, the motor commands are loaded in as a CSV which can be saved on the device memory. The read commands task reads a chunk of the file at a time and shares it with the write commands task. This way, the system will not get a memory error for larger drawings. The task diagram for this operation is shown below.
![alt text](https://github.com/ctgillespie/StrawberryPicker/blob/main/Photos/TaskDiagram.PNG?raw=true "Task Diagram")
## Demonstration
