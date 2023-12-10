# Usage
This is a project by Kai Ang, Kelsen Ma, and Soham Upadeo for WashU's CSE 521S class project, aiming to assist individuals with subjective congnitive decline with basic daily tasks; in this case making oatmeal. In this project, we utilize 2 data models — one for Bluetooth IoT and one for Computer Vision — to decide if certain items are on the table or not. The Bluetooth IoT model requires 3 beacons connected via USB and Computer Vision requires a webcam pointed at the table. If you do not have the required components/setup to run a model, you can turn it off by commenting the relevant lines. There are boolean flags at the top of `app.py` to activate/deactivate these models.
```
# IoT Model requires 3 beacons connected via USB
IOT_ACTIVE = True
# CV requires a webcam
CV_ACTIVE = True
```
## Installing Dependencies
Our project utilizes the following python libraries. Use `pip install <library_name>` to install:
- ultralytics (YoloV8)
- Flask
- pyttsx3
- pyserial
## Setting up IoT
The IoT devices used are Raspberry Pi Pico W's. We define tags to be the devices connected to objects of interest, and beacons as devices connected to the central computer. The tags are loaded with `src/iot/gap/tag.py`. The name of the tag must be changed to the unique item label used by the system:
```
NAME = "test_tag"
```
If using with our CV pre-train, be sure to use the same labels that are used for the required items in the pre-train:
-   "oatmeal"
-   "salt"
-   "measure cup"
-   "1-2 measure cup"
-   "1-4 measure spoon"
-   "pan"
-   "stirring spoon"
-   "timer"
-   "bowl"
-   "metal spoon"
-   "hot_pad"

And we have the following distractors:
-   "scissor"
-   "coke"
-   "book"

Then the beacons must be loaded with `src/iot/gap/beacon.py`. There is no need to alter the script when loading it onto the pi's. Instead, we need to be careful about which port it gets connected to on our system. Figure out which port the devices are connected to, and update the addresses in `iot/gap/iot_model.py`. Two should go on the table, and one should go in the box.
```
# USB Addresses of Beacons
TABLE_0_ADDRESS = "/dev/cu.usbmodem1401"
TABLE_1_ADDRESS = "/dev/cu.usbmodem1301"
BOX_ADDRESS = "/dev/cu.usbmodem1201"
```
Make sure that the scripts are saved on the Pi's as `main.py`. For further help setting up/flashing the Pi's, see: https://projects.raspberrypi.org/en/projects/get-started-pico-w/1.
## Setting up CV
Our model assumes that anything in frame of the camera is on the table, so be sure to point the camera at the table surface. If using our pre-train, make sure the camera is around 3-4 feet above the table surface, pointing down at approximately a 45 degree or steeper angle. Currently, the model uses our pretrain, `beta2.pt`, and the default webcam, `0`:
```
yolo_model = cv.YoloInference(internal_model, model_path="beta2.pt")
```
To use your own pretrain, modify the `model_path` argument of the `YoloInference` object in `app.py`. The pretrain file should be placed in `rsrc/model`. If the wrong webcam is being used, try to change the `webcam_id` argument.
## Running the program
To run the program, from the repo directory, run `python3 app.py`. After a breif setup time, a URL should show up in the terminal, pointing to the endpoint at which the visualizer is being hosted:
```
Running
 * Serving Flask app 'src.tooling.backend'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```
Go to this endpoint to see the model state. You should see something like this:
![image](https://github.com/Kai-WashU/CSE521S/assets/71088632/47c24b31-a626-4c47-aae3-972af5d898bc)
In this image, you can see two images at the top. The one on the left is a live feed from the webcam, and the one on the right is the annotated image from the CV model. Below are three lists labeled according to what they represent. Each entry in the list corresponds to the confidence score of each item, from 0-100. At a certain score, the item will be considered present. For required items, they will be moved from the missing list to the acquired list at this point. For distractors, the third argument in the entry will flip from false to true. Once deemed present, if the score dips below some other threshold, the item will be deemed no longer present. These thresholds can be modified in `src/internal/internal_model.py`:
```
ENABLE_THRESHOLD = 50
DISABLE_THRESHOLD = 30
```
We can also alter the natrual decay of these scores over time:
```
DECAY_FACTOR = 1
```
Score range:
```
MAX_SCORE = 100
```
As well of the influence of each data model. These factors can be found in the data model files themselves. In `src/iot/gap/iot_model.py`:
```
CONFIDENCE_FACTOR = 0.2
```
And in `src/cv/yolo_inference.py`:
```
CONFIDENCE_FACTOR = 1
```
These default settings make IoT roughly 16 times more influential than CV. In different environments/conditions, the reliability of each model may change, so it is important to dial in the decay factor and confidence factors appropriately.
