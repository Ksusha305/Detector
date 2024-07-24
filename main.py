import cv2
from deepface import DeepFace
import numpy as np
from matplotlib import pyplot as plt
import time
import tkinter as tk
window = tk.Tk()
window.title("system")
window.configure(background='black')
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

message = tk.Label(
    window,
    text="Детектор состояния человека",
    bg='black',
    fg='#b0f',
    width=50,
    height=3,
    font=('times', 30, 'bold')
)
message.place(x=350, y=0)

def RecEm():
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise IOError("Cannot open webcam")



    while True:
        ret, frame = cap.read()
        result = DeepFace.analyze(frame, actions=['emotion'])
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.1, 4)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame,
                    str(result[0]['dominant_emotion']),
                    (50, 50),
                    font, 2,
                    (0, 0, 255),
                    2,
                    cv2.LINE_4)
        cv2.imshow('Original video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def RecPul():
    # Camera stream
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1280)
    cap.set(cv2.CAP_PROP_FPS, 30)
    # Video stream (optional)
    # cap = cv2.VideoCapture("videoplayback.mp4")

    # Image crop
    x, y, w, h = 800, 500, 100, 100
    heartbeat_count = 128
    heartbeat_values = [0]*heartbeat_count
    heartbeat_times = [time.time()]*heartbeat_count

    # Matplotlib graph surface
    fig = plt.figure()
    ax = fig.add_subplot(111)

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Our operations on the frame come here
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        crop_img = img[y:y + h, x:x + w]

        # Update the data
        heartbeat_values = heartbeat_values[1:] + [np.average(crop_img)]
        heartbeat_times = heartbeat_times[1:] + [time.time()]

        # Draw matplotlib graph to numpy array
        ax.plot(heartbeat_times, heartbeat_values)
        fig.canvas.draw()
        plot_img_np = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
        plot_img_np = plot_img_np.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        plt.cla()

        # Display the frames
        cv2.imshow('Crop', crop_img)
        cv2.imshow('Graph', plot_img_np)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
takeImg = tk.Button(window, text="Распознать эмоцию",
                    command=RecEm, fg="black", bg="#b0f",
                    width=40, height=3, activebackground="Red",
                    font=('times', 15, ' bold '))
takeImg.place(x=200, y=500)
trainImg = tk.Button(window, text="Распознать пульс",
                     command=RecPul, fg="black", bg="#b0f",
                     width=40, height=3, activebackground="Red",
                     font=('times', 15, ' bold '))
trainImg.place(x=1300, y=500)
window.mainloop()