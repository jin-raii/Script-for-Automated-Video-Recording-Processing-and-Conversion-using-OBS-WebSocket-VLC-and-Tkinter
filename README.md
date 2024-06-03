
# Automated Video Recording, Processing, and Conversion using OBS WebSocket, VLC, and Tkinter

## Introduction

This script automates video recording, processing, and conversion using OBS WebSocket, VLC, and Tkinter. It starts/stops OBS recordings, handles events, manages files, and compresses videos from `.mkv` to `.mp4`. A Tkinter GUI allows users to select output folders and track conversion progress. This script can work in both network and local environments.

## Setting Up the Environment

### Step 1: Create a Virtual Environment

To create a virtual environment, use the following command:

```sh
python -m venv /path/to/your/venv
```
### Step 2: Activate the Virtual Environment

Activate your virtual environment with the following command:

```sh
.\venv\Scripts\activate
```
You should see your virtual environment name on the left side of your terminal or command prompt.

### Step 3: Install Required Packages

Install the obs-websocket-py package using pip:

```sh
pip install obs-websocket-py
```
For more detailed information and documentation, I strongly recommend visiting the [obs-websocket-py](https://github.com/Elektordi/obs-websocket-py) GitHub page.

### Step 4: Install VLC Media Player
Make sure VLC media player is installed on your machine. You can download VLC from [here](https://www.videolan.org/vlc/download-windows.wa.html).

### Step 5: Download and Install OBS WebSocket
- Download OBS WebSocket and install it on your machine from [here](https://github.com/obsproject/obs-websocket/releases). Make sure OBS WebSocket is running.

- Open OBS. If it is already open, close it and open it again to take effect on OBS WebSocket. Go to `Tools` and `WebSocket Server Settings`, then set the `port` of your choice and a `password`. The default `port` is `4444`. We need this information later to connect the Python script to OBS WebSocket.

### Step 6: Modify Output Paths in JSON File
To modify the output paths, edit the options.json file. Change the paths to your desired locations:

```sh
{
  "early_morning": "//path/to/your/network/destination",
  "morning": "//path/to/your/network/destination",
  "evening": "//path/to/your/network/destination"
}
```
This JSON file maps the keys shown on the GUI to the desired output paths. Make sure to provide the correct paths according to your system setup. It can be either on your network path or local path. 

### Script Overview
- This script provides an automated workflow for video recording, processing, and conversion using OBS WebSocket, VLC, and Tkinter. It facilitates the following:

### Automated Recording with OBS
- Start and stop video recording via OBS (Open Broadcaster Software) using OBS WebSocket.
### Event Handling
- Handle recording start and stop events to trigger subsequent actions.
### File Management
- Automatically detect the latest recorded video file.
- Calculate the duration of the recording.
### User Interaction
- Use Tkinter to create a user interface for selecting output folders and displaying progress.
- Allow users to select different output paths for saving recordings.
### Video Conversion
- Compress recorded videos from .mkv to .mp4 format using VLC.
Display a progress bar during video conversion.
### Logging and Error Handling
  - Log detailed information and errors for troubleshooting.
  - This script ensures a seamless process from recording to saving the final processed video, making it ideal for educational institutions, content creators, and anyone needing automated video management         solutions.


