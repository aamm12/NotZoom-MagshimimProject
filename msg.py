import socket
import threading
#chat class
class Msg:
	def __init__(self):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect(('127.0.0.1', 12346))

	def set_aes(self, aes):
		self.aes = aes

	def get_d(self, code, aes):
		self.s.send(code)
		data = self.s.recv(1024)
		if(data == b"-"):
			return []
		data = data[1:]
		data = data.split(b'\xff')
		if aes:
			for i in range(len(data[:-1])):
				data[i] = self.aes.dec_ecb(data[i])
		return data[:-1]

	def send(self, data, code, aes):
		if aes:
			data = self.aes.enc_ecb(data)
		self.s.send(code+data)

	def send_b(self, data):
		self.s.send(data)

	def rec_b(self):
		return self.s.recv(1024)