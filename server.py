import socket 
from _thread import *
import threading 
import struct
import time
import uuid

class Server:

	users = {}
	rooms = {}
	msgs = {}
	videos = {}
	encs = {}
	quizs = {}

	def __init__(self, host="127.0.0.1", port_u=12345, port_t=12346, port_audio=12347, port_screen=12348):
		self.host = host
		self.port_u = port_u
		self.port_t = port_t
		self.port_audio = port_audio
		self.port_screen = port_screen

	def __create_room(self, c):
		uid = str(uuid.uuid4())
		self.rooms[uid] = []
		self.rooms[uid].append(c)
		user_id = str(len(self.rooms[uid])).zfill(3).encode()
		host, port = c.getpeername()
		self.users[host] = [uid, user_id]
		c.send(b'\x01'+user_id+uid.encode())

	def __join_room(self, c, data):
		if data in self.rooms.keys():
			host, port = c.getpeername()
			self.rooms[data].append(c)
			user_id = str(len(self.rooms[data])).zfill(3).encode()
			host, port = c.getpeername()
			self.users[host] = [data, user_id]
			c.send(b'\x01'+user_id)
		else:
			c.send(b'\x00')

	def __leave(self, c):
		host, port = c.getpeername()
		data = self.users[host][0]
		del self.users[host]
		self.rooms[data].remove(c)
		if len(self.rooms[data]) == 0:
			del self.rooms[data]

	def __get_users(self, c):
		host, port = c.getpeername()
		uid = self.users[host][0]
		users_id = []
		for user in self.users.keys():
			if self.users[user][0] == uid:
				users_id.append(self.users[user][1])
		users_str = ",".join(users_id)
		c.send(b'\x01'+users_str.encode())

	def __set_enc(self, c, data):
		host, port = c.getpeername()
		uid = self.users[host][0]
		self.encs[uid] = data

	def __get_enc(self, c):
		host, port = c.getpeername()
		uid = self.users[host][0]
		c.send(self.encs[uid])

	def __add_video(self, c, data):
		host, port = c.getpeername()
		uid = self.users[host][0]
		if uid not in self.videos.keys():
			self.videos[uid] = b"-"
		self.videos[uid] += data + b"\xff"

	def __get_video(self, c):
		host, port = c.getpeername()
		uid = self.users[host][0]
		if uid not in self.videos.keys():
			self.videos[uid] = b"-"
		c.send(self.videos[uid])

	def __add_quiz(self, c, data):
		host, port = c.getpeername()
		uid = self.users[host][0]
		if uid not in self.quizs.keys():
			self.quizs[uid] = b"-"
		self.quizs[uid] += data + b"\xff"

	def __get_quiz(self, c):
		host, port = c.getpeername()
		uid = self.users[host][0]
		if uid not in self.quizs.keys():
			self.quizs[uid] = b"-"
		c.send(self.quizs[uid])

	def __threaded_tcp(self, c):
		while True:
			data = c.recv(1024)
			if data[0] == 1:
				self.__create_room(c)
			elif data[0] == 2:
				self.__join_room(c, data[1:].decode())
			elif data[0] == 3:
				self.__leave(c)
			elif data[0] == 4:
				self.__get_users(c)
			elif data[0] == 5:
				self.__set_enc(c, data[1:])
			elif data[0] == 7:
				self.__get_enc(c)
			elif data == b'\x06':
				host, port = c.getpeername()
				uid = self.users[host][0]
				if uid not in self.msgs.keys():
					self.msgs[uid] = b"-"
				c.send(self.msgs[uid])
			elif data[0] == 8:
				self.__add_video(c, data[1:])
			elif data[0] == 10:
				self.__get_video(c)
			elif data[0] == 11:
				self.__add_quiz(c, data[1:])
			elif data[0] == 12:
				self.__get_quiz(c)
			elif data[0] == 9:
				host, port = c.getpeername()
				uid = self.users[host][0]
				if uid not in self.msgs.keys():
					self.msgs[uid] = b"-"
				self.msgs[uid] += data[1:] + b"\xff"
		c.close()

	def __handle_udp(self, addr, data):
		uid = self.users[addr[0]][0]
		for user in self.users.keys():
			if self.users[user][0] == uid:
				self.send_udp.sendto(data, (user, 9999))
				"""if(self.users[user] != addr[0]):
					self.send_udp.sendto(data, (user, 9999))"""


	def __handle_audio(self, addr, data):
		uid = self.users[addr[0]][0]
		for user in self.users.keys():
			if self.users[user][0] == uid:
				self.send_audio.sendto(data, (user, 9998))
				"""if(self.users[user] != addr[0]):
					self.send_audio.sendto(data, (user, 9999))"""

	def __handle_screen(self, addr, data):
		uid = self.users[addr[0]][0]
		for user in self.users.keys():
			if self.users[user][0] == uid:
				self.send_screen.sendto(data, (user, 9997))
				"""if(self.users[user] != addr[0]):
					self.send_audio.sendto(data, (user, 9999))"""


	def __start_udp_server(self):
		self.send_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
		self.s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
		self.s_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.s_udp.bind((self.host, self.port_u))
		print("udp binded to port", self.port_u)
		try:
			while True:
				data, addr = self.s_udp.recvfrom(200000)
				self.__handle_udp(addr, data)
		except Exception as e: 
			print(e)

	def __start_audio_server(self):
		self.send_audio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
		self.s_audio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
		self.s_audio.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.s_audio.bind((self.host, self.port_audio))
		print("audio binded to port", self.port_audio)
		try:
			while True:
				data, addr = self.s_audio.recvfrom(200000)
				self.__handle_audio(addr, data)
		except Exception as e: 
			print(e)

	def __start_tcp_server(self):
		self.s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		self.s_tcp.bind((self.host, self.port_t))
		print("socket binded to port", self.port_t)
		self.s_tcp.listen(5) 
		print("socket is listening") 
		while True: 
			c, addr = self.s_tcp.accept() 
			start_new_thread(self.__threaded_tcp, (c,))

	def __start_screen_server(self):
		self.send_screen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
		self.s_screen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
		self.s_screen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.s_screen.bind((self.host, self.port_screen))
		print("screen binded to port", self.port_screen)
		try:
			while True:
				data, addr = self.s_screen.recvfrom(200000)
				self.__handle_screen(addr, data)
		except Exception as e: 
			print(e)

	def run(self):
		self.tcp_server_th = threading.Thread(target=self.__start_tcp_server)
		self.udp_server_th = threading.Thread(target=self.__start_udp_server)
		self.audio_server_th = threading.Thread(target=self.__start_audio_server)
		self.screen_server_th = threading.Thread(target=self.__start_screen_server)
		self.tcp_server_th.start()
		self.udp_server_th.start()
		self.audio_server_th.start()
		self.screen_server_th.start()
		command = ""
		while command != "EXIT":  # commands to help us control the server while develop
			command = input()
			if command == "CLOSE_TCP":
				self.s_tcp.close()
				print("tcp close")
			elif command == "OPEN_TCP":
				self.tcp_server_th = threading.Thread(target=self.__start_tcp_server)
				self.tcp_server_th.start()
				print("tcp open")
			elif command == "CLOSE_UDP":
				self.s_udp.close()
				print("udp close")
			elif command == "OPEN_UDP":
				self.udp_server_th = threading.Thread(target=self.__start_udp_server)
				self.udp_server_th.start()
				print("udp open")
			elif command == "EXIT":
				self.s_udp.close()
				self.s_tcp.close()
				self.s_audio.close()
		print("sockets closed")