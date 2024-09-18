import cv2
from lib.device import Camera
from lib.interface import plotXY
from lib.processors_noopenmdao import findFaceGetPulse
import sys
serial = None
baud = None
send_serial = False
udp = None
send_udp = False
plot_title = "Data display - raw signal (top) and PSD (bottom)"


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
    cv2.namedWindow(plot_title)
    cv2.moveWindow(plot_title, w, 0)


def make_bpm_plot():
    plotXY([[processor.times,
             processor.samples],
            [processor.freqs,
             processor.fft]],
           labels=[False, True],
           showmax=[False, "bpm"],
           label_ndigits=[0, 0],
           showmax_digits=[0, 1],
           skip=[3, 3],
           name=plot_title,
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
processor = findFaceGetPulse(bpm_limits=[70, 160], data_spike_limit=2500., face_detector_smoothness=10.)
cap = cv2.VideoCapture(0)
def sdf():
    ret, frame = cap.read()
    if ret:
        processor.frame_in = frame
        processor.run(selected_cam)
        toggle_display_plot()
        key_handler()
while True:
    sdf()