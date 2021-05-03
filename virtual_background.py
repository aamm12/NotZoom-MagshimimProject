import tensorflow as tf
import cv2
import numpy as np
from tf_bodypix.api import download_model, load_model, BodyPixModelPaths
from numba import jit
from video import resize_video

@jit(nopython=True)
def virtual(frame, mask, background):
    virtual_frame = frame
    for i in range(len(mask)):
        for j in range(len(mask[i])):
            if (mask[i][j] == 0):
                virtual_frame[i][j] = background[i][j]
    return virtual_frame


class VirtualBackground():
    def __init__(self):
        self.bodypix_model = load_model(download_model(
            BodyPixModelPaths.MOBILENET_FLOAT_50_STRIDE_16
        ))
        self.background = None

    def set_name(self, name):
        self.background = cv2.imread(name)

    def add_virtual_background(self, frame):
        tmp_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.bodypix_model.predict_single(tmp_img)
        mask = result.get_mask(threshold=0.75)
        mask = np.array(mask)
        mask = mask.reshape((frame.shape[0], frame.shape[1]))
        if self.background.shape[0] != frame.shape[0]:
            self.background = resize_video(self.background, frame.shape[0], frame.shape[1])
        return virtual(frame, mask, self.background)
