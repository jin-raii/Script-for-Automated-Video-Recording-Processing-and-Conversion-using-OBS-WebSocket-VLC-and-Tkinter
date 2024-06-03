import time
import subprocess
import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog
import json
import logging
import queue
from datetime import datetime
from obswebsocket import obsws, events, requests
import tkinter.messagebox as messagebox

logging.basicConfig(level=logging.DEBUG)

host = "localhost"
port = 4444
password = "Iracad3my"
output_folder = r"path\to\your\videos"
logo = 'logo.ico'

vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"

recording_filename = ""
recording_start_time = None
recording_stop_time = None


def prompt_for_output_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_selected = filedialog.askdirectory(title="Select Output Folder for Compressed Videos")
    root.destroy()
    return folder_selected


def on_event(event):
    global recording_filename, recording_start_time, recording_stop_time

    logging.debug(f"Got event: {event}")

    if isinstance(event, events.RecordingStarted):
        logging.info("Recording started...")
        recording_start_time = datetime.now()
    elif isinstance(event, events.RecordingStopped):
        logging.info("Recording stopped...")
        recording_stop_time = datetime.now()
        recording_filename = get_latest_recording()
        if recording_filename:
            logging.info(f"Latest recording found: {recording_filename}")
            logging.info("Starting video conversion...")
            progress_var = tk.DoubleVar()
            duration = calculate_recording_duration()
            completion_queue = queue.Queue()
            root.after(100, lambda: start_recording_options(progress_var, duration, completion_queue))
        else:
            logging.error("No recording found.")

def get_latest_recording():
    recordings = [os.path.join(output_folder, file) for file in os.listdir(output_folder) if file.endswith('.mp4')]
    if recordings:
        return max(recordings,  key=os.path.getctime)
    else:
        return None

def calculate_recording_duration():
    if recording_start_time and recording_stop_time:
        duration = (recording_stop_time - recording_start_time).total_seconds()
        logging.info(f"Calculated recording duration: {duration} seconds")
        return duration
    return None



def load_options_from_json(file_path):
    with open(file_path, 'r') as json_file:
        return json.load(json_file)

options = load_options_from_json('options.json')

def start_recording_options(progress_var, duration, completion_queue):
    def set_recording_slot(slot):
        selected_output_folder = options[slot]
        logging.info(f"Recording option selected: {slot}")
        option_window.destroy()  # Close the option window
        convert_with_progressbar(recording_filename, selected_output_folder)

    option_window = tk.Toplevel(root)
    option_window.title("Choose Recording Path")
    option_window.iconbitmap(logo)
    option_window.geometry("300x200")

    label = tk.Label(option_window, text="Select your class for saving recording file :", font=("Helvetica", 12))
    label.pack(pady=10)

    for slot, folder_path in options.items():
        button = tk.Button(option_window, text=slot.capitalize(), command=lambda s=slot: set_recording_slot(s))
        button.pack(pady=5)

# compress video .mkv to .mp4
def compress_video(file_path, selected_output_folder, progress_var, duration, completion_queue):
    if not file_path:
        logging.error("No file to compress.")
        return

    file_name = os.path.basename(file_path)
    current_date = datetime.now().strftime("%m_%d_%Y")
    output_folder = os.path.join(selected_output_folder, current_date)  # Use selected_output_folder directly
    logging.info(f"Output folder: {output_folder}")

    os.makedirs(output_folder, exist_ok=True)

    output_file = os.path.join(output_folder, "_" + file_name)
    logging.info(f"Output file: {output_file}")

    vlc_command = [
        vlc_path,
        "-I", "dummy",
        "-v", file_path,
        "--sout=#transcode{vcodec=h264,vb=1024,acodec=mp4a,ab=192,channels=2,deinterlace}:standard{access=file,mux=mp4,dst=" + output_file + "}",
        "vlc://quit"
    ]

    logging.info(f"VLC command: {' '.join(vlc_command)}")

    try:
        start_time = time.time()
        process = subprocess.Popen(vlc_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time >= duration:
                break
            progress_var.set(min(elapsed_time / duration * 100, 100))
            time.sleep(1)

        stdout, stderr = process.communicate()
        logging.info(f"VLC output: {stdout}")
        logging.info(f"VLC errors: {stderr}")

        if process.returncode == 0:
            completion_queue.put("done")
            messagebox.showinfo("Conversion Done", f"Video conversion done. Compressed video saved to:\n{output_file}")

            # Remove the original recorded video
            os.remove(file_path)
            logging.info(f"Original recorded video deleted: {file_path}")
        else:
            logging.error(f"VLC command failed with return code {process.returncode}")
    except Exception as e:
        logging.error(f"Error compressing video: {e}")
    finally:
        completion_queue.put("done")

# show progress bar 
def convert_with_progressbar(file_path, selected_output_folder):
    progress_window = tk.Toplevel(root)
    progress_window.title("Convert Video")
    progress_window.iconbitmap(logo)
    progress_window.geometry("300x100")

    progress_label = tk.Label(progress_window, text="Converting Video...", font=("Helvetica", 12))
    progress_label.pack(pady=10)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
    progress_bar.pack(fill=tk.X, padx=20)

    duration = calculate_recording_duration()
    if duration is None:
        duration = 100  # Fallback to a default duration

    completion_queue = queue.Queue()

    def run_compression():
        compress_video(file_path, selected_output_folder, progress_var, duration, completion_queue)

    progress_thread = threading.Thread(target=run_compression)
    progress_thread.start()

    def check_completion_queue():
        try:
            msg = completion_queue.get_nowait()
            if msg == "done":
                progress_window.destroy()
        
        except queue.Empty:
            root.after(100, check_completion_queue)

    root.after(100, check_completion_queue)

def start_recording():
    logging.info("Starting recording...")
    ws.call(requests.StartRecording())

def stop_recording():
    logging.info("Stopping recording...")
    ws.call(requests.StopRecording())

ws = obsws(host, port, password)
ws.register(on_event, events.RecordingStarted)
ws.register(on_event, events.RecordingStopped)
ws.connect()

# GUI 
root = tk.Tk()
root.withdraw()
root.iconbitmap(logo)



try:
    logging.info("Connected to OBS WebSocket")
    root.mainloop()
except KeyboardInterrupt:
    pass
finally:
    ws.disconnect()
