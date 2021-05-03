import cv2
import numpy as np
import pyautogui
from video import resize_video

def screen_cap(udp_send, user_id):
    img = pyautogui.screenshot()
    frame = np.array(img)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = resize_video(frame, 270, 480)
    udp_send.send_frame(frame, user_id+100)