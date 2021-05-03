import pyaudio
import socket
import time

class Audio:
	def __init__(self):
		self.mic = True
		self.lis_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
		self.lis_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.lis_sock.bind(("127.0.0.1", 9998))
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		#self.sock.sendto("add_user".encode(), ("127.0.0.1", 12347))
		self.chunk = 1024  # Record in chunks of 1024 samples
		sample_format = pyaudio.paInt16  # 16 bits per sample
		channels = 2
		fs = 44100  # Record at 44100 samples per second
		self.p = pyaudio.PyAudio()

		self.stream_paly = self.p.open(format=sample_format, channels=channels, rate=fs, output = True)
		self.stream_lis = self.p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=self.chunk, input=True)

	def record(self):
		data = self.stream_lis.read(self.chunk) # get the audio
		self.sock.sendto(data, ("127.0.0.1", 12347))
		time.sleep(0.01)


	def get_audio(self):
		while True:
			data, addr = self.lis_sock.recvfrom(200000)
			if data != b'':
				self.stream_paly.write(data)

	def mic_c(self):
		self.mic = not self.mic
		print(self.mic)

	def __del__(self):
		# Stop and close the stream_lis 
		self.stream_paly.stop_stream()
		self.stream_lis.stop_stream()
		self.stream_paly.close()
		self.stream_lis.close()
		# Terminate the PortAudio interface
		self.p.terminate()
