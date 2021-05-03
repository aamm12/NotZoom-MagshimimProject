import socket
import numpy as np
import pickle
import cv2
import struct
import threading
import time
from numba import jit
import base64

@jit(forceobj=True, parallel=True)
def list_e(l):
    for i in l:
        if i is None:
            return False
    return True

@jit(forceobj=True, parallel=True)
def connect_frame(frame):
    new_frame = frame[0]
    for i in frame[1:]:
        new_frame = np.concatenate((new_frame, i), axis=0)
    return new_frame

@jit(forceobj=True, parallel=True)
def build_frame(frames: np.ndarray, users: np.ndarray, data: bytes):
    user_id = int(data[3:6])
    if users[user_id] is not None:
        users[user_id][int(data[0:3])] = pickle.loads(data[6:])
        if list_e(users[user_id]):
            new_frame = connect_frame(users[user_id])
            frames[user_id] = new_frame
    else:
        users[user_id] = np.empty(10,  dtype=np.ndarray)
        users[user_id][int(data[0:3])] = pickle.loads(data[6:])

class SendVideo:


    def __init__(self, ip_host, ip_me, port, port_me):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.lis_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
        self.lis_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lis_sock.bind((ip_me, port_me))
        #self.sock.sendto("add_user".encode(), (ip_host, port))
        self.ip = ip_host
        self.port = port

    def __create_img_packet(self, frame_part, index, user_id):
        data = b""
        data += str(index).zfill(3).encode()
        data += str(user_id).zfill(3).encode()
        data += pickle.dumps(frame_part)
        return data

    """def send_frame(self, frame, user_id):
                    for i in range(len(frame)):
                        self.sock.sendto(self.__create_img_packet(frame[i], i, user_id), (self.ip, self.port))
                        time.sleep(0.000001)"""

    def send_frame(self, frame, user_id):
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame1 = jpeg.tobytes()
        self.sock.sendto(str(user_id).zfill(3).encode()+frame1, (self.ip, self.port))
    """def get_frame(self):
                    while True:
                        data, addr = self.lis_sock.recvfrom(200000)
                        frame = pickle.loads(data[3:])
                        for i in range(9):
                            data, addr = self.lis_sock.recvfrom(200000)
                            frame = np.concatenate((frame, pickle.loads(data[3:])), axis=0)
                        cv2.imshow('frame',frame)
                        frame = None
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    cv2.destroyAllWindows()"""

    """def get_frame(self, frames):
                    users = np.empty(1000,  dtype=np.ndarray)
                    while True:
                        data, addr = self.lis_sock.recvfrom(200000)
                        build_frame(frames, users, data)"""

    def get_frame(self, frames):
        while True:
            data, addr = self.lis_sock.recvfrom(200000)
            frames[int(data[:3])] = data[3:]
