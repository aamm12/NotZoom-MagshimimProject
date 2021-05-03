import numpy as np
import cv2
import speedtest
import threading
from numba import jit

@jit
def resize_video(img,m,n):  # k-Nearest Neighbors algorithm
    height,width,channels =img.shape
    resized_image=np.zeros((m,n,channels),np.uint8)
    sh=m/height
    sw=n/width
    for i in range(m):
        for j in range(n):
            x=int(i/sh)
            y=int(j/sw)
            resized_image[i,j]=img[x,y]
    return resized_image

class Video:
	speed = 0
	def __init__(self):
		x = threading.Thread(target=self.__get_net_speed)
		x.start()

	def __get_net_speed(self):
		st = speedtest.Speedtest()
		while True:
			self.speed = st.download()

	def set_capture(self, fps=30, width=320, height=240):
		self.capture = cv2.VideoCapture(0)
		self.capture.set(cv2.CAP_PROP_FPS, fps)
		self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
		self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

	def capture_video(self):
		ret, frame = self.capture.read()
		frame_fix = cv2.flip(frame, 1)
		if(self.speed > 0 and self.speed < 25000000):
			frame_fix = resize_video(frame_fix, 120, 160)
		return(frame_fix)
