from moviepy.config import get_setting
import subprocess as sp
from time import sleep
import tkinter as tk
from datetime import datetime
import threading
import pyautogui

audio_devices_cmd = [
    get_setting("FFMPEG_BINARY"),
    '-list_devices','true','-f','dshow','-i','dummy'
]
# sp.run(audio_devices_cmd)

audio_devices = ["Microphone Array (Realtek(R) Audio)","Stereo Mix (Realtek(R) Audio)"]

cmd = [
    get_setting("FFMPEG_BINARY"),
    '-y',
    '-probesize','100M',
    '-fflags', '+genpts',
    '-f','gdigrab',
    '-thread_queue_size','4096',
    '-draw_mouse','1',
    '-i','desktop',
    # '-video_size','1920x1080',
    '-f','dshow',
    '-thread_queue_size','4096',
    '-rtbufsize','50M',
    '-i',f'audio={audio_devices[0]}',
    '-f','dshow',
    '-thread_queue_size','4096',
    '-rtbufsize','50M',
    '-i',f'audio={audio_devices[1]}',
    '-flush_packets','1',
    '-filter_complex',"[1:a]adelay=500|500[mic];[mic]aformat=channel_layouts=stereo[mic]; [mic]anlmdn=s=1:o=o[mic];[mic]volume=2.0[mic]; [mic]aformat=sample_fmts=fltp:channel_layouts=stereo[micout] ;[2:a]adelay=1500|1500[sys];[sys]aformat=channel_layouts=stereo[sys]; [micout][sys]amerge=inputs=2[aout]",
    '-map','0:v','-map','[aout]',
    '-c:v','libx264',
    '-preset','ultrafast',
    '-c:a','libmp3lame',
    # '-b:a','192k'
    '-pix_fmt','yuv420p',
    '-movflags','faststart',
    # '-t',str(30),
    # "test.mp4"
]

# sp.run(cmd)

# result = sp.Popen(cmd,stdin=sp.PIPE)
# sleep(5)
# result.stdin.write(b'q')
# result.stdin.flush()
# result.wait()

recorder = None
st = None
rec = False
root = tk.Tk()
width = 500
height = 35

# Get screen dimensions
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (width // 2)
y = 0
root.geometry(f"{width}x{height}+{x}+{y}")


root.attributes("-topmost", True)

root.overrideredirect(True)


root.configure(background='black')

label = tk.Label(root, text="Start...", font=("Arial", 12), fg="white", bg="black")
label.pack(side='left',padx=150)
canvas_width = 30
canvas_height = canvas_width
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="black", highlightthickness=0)
canvas.pack()
center_x = canvas_width // 2
center_y = canvas_height // 2
radius = canvas_width // 2 - 2 
oval_id = canvas.create_oval(center_x - radius, center_y - radius,
                             center_x + radius, center_y + radius,
                             fill="green")

timerthread = None
def startrec_click(event):
    global recorder,st,button_frame,canvas,rec,label,timerthread,square_canvas
    cmd.extend([
        f'PWP_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.mp4'
    ])
    recorder = sp.Popen(cmd,stdin=sp.PIPE)
    sleep(0.1)
    st = datetime.now()
    canvas.pack_forget()
    button_frame.pack()
    square_canvas.pack()
    rec = True
    timerthread = threading.Thread(target=updatetime)
    timerthread.daemon = True
    timerthread.start()

button_frame = tk.Frame(root, bg="black")
canvas.tag_bind(oval_id, "<Button-1>", startrec_click)

square_width = 30 
square_canvas = tk.Canvas(button_frame, width=square_width, height=square_width, bg="yellow", highlightthickness=0)
square_id = square_canvas.create_rectangle(0, 0, square_width, square_width, fill="red")  

def stoprec_click(event):
    global recorder,rec,canvas,button_frame,label,timerthread,square_canvas
    recorder.stdin.write(b'q')
    recorder.stdin.flush()
    rec = False
    cmd.pop()
    button_frame.pack_forget()
    square_canvas.pack_forget()
    recorder.wait()
    print("stopped")
    canvas.pack()
    
square_canvas.tag_bind(square_id, "<Button-1>", stoprec_click)

def stop_rec():
    global recorder,root
    recorder.stdin.write(b'q')
    recorder.stdin.flush()
    recorder.wait()
    root.destroy()
    
def hide_window():
    root.withdraw()

# Function to show the window
def show_window():
    root.deiconify()

def updatetime():
    print("update time started")
    global label,st,rec
    while rec:
        diff = str(datetime.now()-st)
        diff = diff.split(':')
        label.config(text=f"REC...{diff[0]}:{diff[1]}:{int(diff[2].split('.')[0])}")
    label.config(text="Start")
    

def on_mouse_motion():
    while True:
        event = pyautogui.position()
        x, y = event.x, event.y
        # print(x,y)
        if screen_width // 2 - width // 2 <= x <= screen_width // 2 + width // 2 and y == 0:
            show_window()
            while True:
                event = pyautogui.position()
                x, y = event.x, event.y
                if screen_width // 2 - width // 2 <= x <= screen_width // 2 + width // 2 and y <= 35:
                    show_window()
                else:
                    break
        else:
            hide_window()
            # pass


mousethread = threading.Thread(target=on_mouse_motion)
mousethread.daemon = True
mousethread.start()
root.mainloop()