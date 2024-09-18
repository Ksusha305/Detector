import tkinter as tk
import customtkinter as Ctk
from customtkinter import *
import cv2
from PIL import Image, ImageTk
from fer import FER
from lib.device import Camera
from lib.interface import plotXY
from lib.processors_noopenmdao import findFaceGetPulse
import sys
serial = None
baud = None
send_serial = False
udp = None
send_udp = False
from  lib.processors_noopenmdao import t
# plot_title = "Data display - raw signal (top) and PSD (bottom)"


def key_handler():
    cv2.waitKey(10) & 255
    # if pressed == 27:
    #     print("Exiting")
    #     for cam in cameras:
    #         cam.cam.release()
    #     if send_serial:
    #         serial.close()
    #     sys.exit()


def toggle_search():
    state = processor.find_faces_toggle()
    print("face detection lock =", not state)


def toggle_display_plot():
    print("bpm plot enabled")
    if processor.find_faces:
        toggle_search()
    make_bpm_plot()
    # cv2.namedWindow(plot_title)
    # cv2.moveWindow(plot_title, w, 0)

win = None
def make_bpm_plot():
    global win
    plotXY([[processor.times,
             processor.samples],
            [processor.freqs,
             processor.fft]],
           labels=[False, True],
           showmax=[False, "bpm"],
           label_ndigits=[0, 0],
           showmax_digits=[0, 1],
           skip=[3, 3],
           bg=processor.slices[0])




if serial:
    send_serial = True
if not baud:
    baud = 9600
else:
    baud = int(baud)
    serial = Serial(port=serial, baudrate=baud)

if udp:
    send_udp = True
    if ":" not in udp:
        ip = udp
        port = 5005
    else:
        ip, port = udp.split(":")
        port = int(port)
    udp = (ip, port)

cameras = []
selected_cam = 0
for i in range(3):
    camera = Camera(camera=i)  # first camera by default
    if camera.valid or not len(cameras):
        cameras.append(camera)
    else:
        break
w, h = 0, 0
pressed = 0
processor = findFaceGetPulse(bpm_limits=[50, 160], data_spike_limit=2500., face_detector_smoothness=10.)
cap = cv2.VideoCapture(0)
def Pulse():
    ret, frame = cap.read()
    if ret:
        processor.frame_in = frame
        processor.run(selected_cam)
        toggle_display_plot()
        key_handler()

Ctk.set_default_color_theme("dark-blue")
app = Ctk.CTk()
width = app.winfo_screenwidth()
height = app.winfo_screenheight()
app.geometry("%dx%d" % (width, height))

window_menu = Ctk.CTkFrame(app, width=width, height=100, fg_color="#c31b1c")
window_menu.pack(side=TOP)
window_menu_text = Ctk.CTkLabel(window_menu,
                                text="Российские железные дороги",
                                width=width,
                                font=("emoji", 50, "bold"))
window_menu_text.pack(side=LEFT, pady=15)

window_web = Ctk.CTkFrame(app, width=900, height=700)
window_web.pack(side=LEFT, padx=70)
label = tk.Label(window_web, width=900, height=700)
label.pack()

cap = cv2.VideoCapture(0)
# face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
emotion_detector = FER(mtcnn=True)
emotions_frame = []
emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
emotions_labels = []
procents_labels = []
index = -1

window_emotions_and_pulse = Ctk.CTkFrame(app, width=300, height=700)
window_emotions_and_pulse.pack(side=RIGHT, padx=70, pady=70)

window_emotions = Ctk.CTkFrame(window_emotions_and_pulse, width=300, height=400)
window_emotions.pack(side=TOP, pady=50, padx=20)

window_pulse = Ctk.CTkFrame(window_emotions_and_pulse, width=300, height=250)
window_pulse.pack(side=BOTTOM, pady=50)
label_pul = tk.Label(window_pulse, width=300, height=250)
label_pul.pack()

for i in range(len(emotions)):
    emotions_frame.append(Ctk.CTkFrame(window_emotions))
    emotions_frame[i]['height'] = 400
    emotions_frame[i]['width'] = 300
    emotions_frame[i].pack(side=TOP, padx=5, pady=5)
for i in range(len(emotions)):
    emotions_labels.append(tk.Label(emotions_frame[i]))
    emotions_labels[i]['text'] = emotions[i]
    emotions_labels[i]['font'] = ("Arial", 25, "bold")
    emotions_labels[i]['background'] = "gray17"
    emotions_labels[i]['foreground'] = "red" if i == index else "white"
    emotions_labels[i]['width'] = 10
    emotions_labels[i].pack(side=LEFT)



def updateFrame():
    global z
    ret, frame = cap.read()
    if ret:
        # processor.frame_in = frame
        # processor.run(0)

        frame = cv2.resize(frame, (600, 400))  # Уменьшенный размер
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        captured_emotions = emotion_detector.detect_emotions(img)
        pr = -1
        for i in range(len(emotions)):
            iii = str(emotions[i])
            if pr < captured_emotions[0]['emotions'][iii]:
                index = i
                pr =captured_emotions[0]['emotions'][iii]
        for i in range(7):
            procents_labels.append(tk.Label(emotions_frame[i]))
            ii = str(emotions[i])
            procents_labels[i]['text'] = f'{captured_emotions[0]['emotions'][ii]*100: .0f}%'
            procents_labels[i]['font'] = ("Arial", 25, "bold")
            procents_labels[i]['background'] = "gray17"
            procents_labels[i]['foreground'] = "red" if i == index else "white"
            procents_labels[i]['width'] = 40
            procents_labels[i].pack(side=RIGHT)
        # if t != None:
        #
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        label.imgtk = imgtk
        label.configure(image=imgtk)
    app.after(50, updateFrame)
    app.after(50, Pulse)


updateFrame()

app.mainloop()
