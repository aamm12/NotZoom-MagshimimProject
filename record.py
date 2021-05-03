import cv2
import numpy as np
import pyautogui

class Record:

    def __init__(self):
        SCREEN_SIZE = (1920, 1080)
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        self.out = cv2.VideoWriter("output.avi", fourcc, 20.0, (SCREEN_SIZE))

    def capture_screen(self):
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.out.write(frame)

    def stop_capture(self):
        self.out.release()