from video import Video, resize_video
from audio import Audio
from msg import Msg
import cv2
from users_manager import User_manage
from send_video import SendVideo
import socket
import numpy as np
from _thread import *
import threading 
from flask import Flask, render_template, Response, request, redirect, url_for, flash, make_response
import multiprocessing
from aes import AES
import time
import uuid
from share_screen import screen_cap
from youtube import get_videos
from virtual_background import VirtualBackground
from record import Record
import os
import base64
import pickle

def capture_video():
    global virtual_background_name
    global virtual_background
    global camera
    global start
    global user_id
    global img
    while True:
        if start:
            if camera:
                frame = video.capture_video()
                if test:
                    frame = resize_video(frame, 120, 160)
                if virtual_background:
                    frame = virtualbackground.add_virtual_background(frame)
                if frame is not None:
                    udp_send.send_frame(frame, user_id)
            else:
                if img is not None:
                    udp_send.send_frame(img, user_id)

def record_screen():
    global record_flag
    while record_flag:
        record.capture_screen()

def capture_screen():
    global screen_flag
    global frames
    while screen_flag:
        screen_cap(screen_send, user_id)

def capture_audio():
    global mic
    global start
    while True:
        if start:
            if mic:
                audio.record()
            else:
                time.sleep(0.01)

def gen(user_frame):
    global frames
    while True:
        if int(user_frame) in frames.keys():
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' +  frames[int(user_frame)] + b'\r\n\r\n')

app = Flask(__name__)

@app.route('/home')
def home():
    global frames
    global camera
    if 'email' in request.cookies:
        room_id = request.cookies.get('room')
        print(frames.keys())
        if not screen_flag:
            if user_id+100 in frames.keys():
                del frames[user_id+100]
        return render_template('index.html',virtual_background=virtual_background, frames=frames, none=None, l=len(frames), room_id=room_id, record_flag=record_flag)
    else:
        flash('to use this app please login')
        return redirect(url_for('login'))

@app.route('/create-room', methods=['POST'])
def create_room():
    global start
    global camera
    global mic
    global user_id
    resp = make_response(redirect(url_for('home')))
    msg.send_b(b'\x01')
    ms = msg.rec_b()
    uid = str(uuid.uuid4()).encode()
    uid = b'\x05' + uid[1:]
    aes_key = uid[1:8] + uid[9:13] + uid[14:18] + bytes([uid[19]])
    aes = AES(aes_key)
    msg.set_aes(aes)
    msg.send_b(b'\x05'+uid)
    user_data = ms[1:].decode()
    resp.set_cookie('room', user_data[3:])
    resp.set_cookie('id', user_data[:3])
    user_id = int(user_data[:3])
    camera = True
    start = True
    mic = False
    time.sleep(1.5)
    return resp

@app.route('/join-room', methods=['POST', 'GET'])
def join_room():
    global start
    global camera
    global mic
    global user_id
    if request.method == 'POST':
        room_id = request.form.get('room_id')
    else:
        room_id = request.args.get('room_id')
    msg.send_b(b'\x02'+room_id.encode())
    ms = msg.rec_b()
    if ms[0] == 1:
        user_data = ms[1:].decode()
        resp = make_response(redirect(url_for('home')))
        resp.set_cookie('room', room_id)
        resp.set_cookie('id', user_data[:3])
        user_id = int(user_data[:3])
        camera = True
        start = True
        mic = False
        msg.send_b(b'\x07')
        uid = msg.rec_b()
        aes_key = uid[1:8] + uid[9:13] + uid[14:18] + bytes([uid[19]])
        aes = AES(aes_key)
        msg.set_aes(aes)
        time.sleep(1.5)
        return resp
    else:
        flash('Invalid room id')
        return redirect(url_for('index'))

@app.route('/leave', methods=['POST'])
def leave():
    global start
    global camera
    global mic
    camera = False
    start = False
    mic = False
    msg.send_b(b'\x03')
    resp = make_response(redirect(url_for('index')))
    resp.delete_cookie("room")
    return resp

@app.route('/screen', methods=['POST'])
def screen():
    global screen_flag
    global frames
    screen_flag = not screen_flag
    if screen_flag:
        capture_screen_th =  threading.Thread(target=capture_screen)
        capture_screen_th.start()
    else:
        del frames[user_id+100]
    time.sleep(1)
    return redirect(url_for('home'))

@app.route('/record', methods=['POST'])
def record():
    global record_flag
    global record
    record_flag = not record_flag
    if record_flag:
        record = Record()
        record_screen_th =  threading.Thread(target=record_screen)
        record_screen_th.start()
    else:
        record.stop_capture()
    time.sleep(1)
    return redirect(url_for('home'))

@app.route('/youtube')
def youtube_v():
    if 'room' in request.cookies:
        return render_template("youtube.html")
    else:
        return redirect(url_for('index'))

@app.route('/background')
def background():
    global virtual_background
    if 'room' in request.cookies:
        if not virtual_background:
            return render_template("virtual_background.html")
        else:
            os.remove(virtual_background_name)
            virtual_background = not virtual_background
            return redirect(url_for('home'))
    else:
        return redirect(url_for('index'))

@app.route('/background', methods=['POST'])
def background_post():
    global virtual_background_name
    global virtual_background
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        virtual_background_name = uploaded_file.filename
        uploaded_file.save(uploaded_file.filename)
        virtualbackground.set_name(virtual_background_name)
        virtual_background = not virtual_background
    return redirect(url_for('home'))

@app.route('/select_video', methods=['POST'])
def select_video():
    name = request.form.get('video_name')
    if "https://" in name or "http://" in name:
        msg.send(base64.b64encode(name.encode()), b'\x08', False)
        return redirect(url_for('home'))
    else:
        videos = get_videos(name)
        return render_template('select_video.html', videos=videos)

@app.route('/set_video')
def set_video():
    url = request.args['src']
    msg.send(base64.b64encode(url.encode()), b'\x08', False)
    return redirect(url_for('home'))

@app.route('/videos')
def videos():
    y_videos = msg.get_d(b'\x0A', False)
    for i in range(len(y_videos)):
        y_videos[i] = base64.b64decode(y_videos[i]).decode()
    return render_template('videos.html', videos=y_videos)

@app.route('/video_feed')
def video_feed():
    user_frame = request.args['user_frame']
    return Response(gen(user_frame),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/create_quiz')
def create_quiz():
    if 'room' in request.cookies:
        return render_template("create_quiz.html")
    else:
        return redirect(url_for('index'))

@app.route('/create_quiz', methods=['POST'])
def create_quiz_post():
    question = {}
    question['question'] = request.form.get('question')
    question['answer1'] = request.form.get('answer1')
    question['answer2'] = request.form.get('answer2')
    question['answer3'] = request.form.get('answer3')
    question['answer4'] = request.form.get('answer4')
    question['correct_answer'] = request.form.get('correct_answer')
    data = pickle.dumps(question)
    print(data)
    msg.send(base64.b64encode(data), b'\x0B', False)
    return redirect(url_for('home'))

@app.route('/quizzes')
def quizzes():
    quizzes_list = msg.get_d(b'\x0C', False)
    for i in range(len(quizzes_list)):
        print(base64.b64decode(quizzes_list[i]))
        quizzes_list[i] = pickle.loads(base64.b64decode(quizzes_list[i]))
    return render_template('quizzes.html', quizzes=quizzes_list)

@app.route('/quizzes', methods=['POST'])
def quizzes_post():
    ans = request.form.get('answer')
    correct_ans = request.form.get('correct_answer')
    if ans != correct_ans:
        flash('incorrect answer')
        return redirect(url_for('quizzes'))
    else:
        return redirect(url_for('home'))


@app.route('/')
def index():
    if 'email' in request.cookies:
        if "id" in request.args:
            room_id = request.args.get('id')
            redirect(url_for('join_room', room_id=room_id))
        else:
            resp = make_response(render_template('base.html'))
            if 'room' in request.cookies:
                resp.delete_cookie("room")
            return resp
    else:
        return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    res = user_manage.add_user(name, email, password)
    if res:
        return redirect(url_for('login'))
    else:
        flash('Email address already exists')
        return redirect(url_for('signup'))

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    user = user_manage.get_user(email, password)
    if user:
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('email', email)
        resp.set_cookie('password', password)
        resp.set_cookie('name',user["displayName"])
        return resp
    flash('check your login info')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('home')))
    resp.delete_cookie("email")
    resp.delete_cookie("password")
    resp.delete_cookie("name")
    return resp

@app.route('/chat')
def chat():
    data1 = msg.get_d(b'\x06', True)
    for i in range(len(data1)):
        data1[i] = data1[i].decode()
    print(data1)
    return render_template('chat.html', len=len(data1), data1=data1)

@app.route('/chat', methods=['POST'])
def post_chat():
    global msg
    data = request.form.get('data')
    msg.send(data.encode(), b'\x09', True)
    return redirect(url_for('chat'))

@app.route('/camera', methods=['POST'])
def camera():
    global camera
    camera = not camera
    return redirect(url_for('home'))

@app.route('/mic', methods=['POST'])
def mic_cc():
    global mic
    mic = not mic
    #audio.mic_c()
    return redirect(url_for('home'))

@app.route('/test')
def test_run():
    global test
    test = not test
    return redirect(url_for('home'))


if __name__ == '__main__':
    camera = False
    mic = False
    start = False
    record_flag = False
    screen_flag = False
    test = False
    virtual_background = False
    virtual_background_name = ""
    user_id = 0
    frames =  {}
    msgs = []
    img = cv2.imread('no_image.png') 
    user_manage = User_manage()
    app.secret_key = 'super secret key'
    udp_send = SendVideo("127.0.0.1" , "127.0.0.1", 12345, 9999)
    screen_send = SendVideo("127.0.0.1" , "127.0.0.1", 12348, 9997)
    video = Video()
    audio = Audio()
    msg = Msg()
    record = Record()
    video.set_capture(30, 320, 240)
    virtualbackground = VirtualBackground()
    send_camera_th =  threading.Thread(target=capture_video)
    send_audio_th =  threading.Thread(target=capture_audio)
    get_audio_th =  threading.Thread(target=audio.get_audio)
    udp_listen_th = threading.Thread(target=udp_send.get_frame, args=(frames, ))
    screen_listen_th = threading.Thread(target=screen_send.get_frame, args=(frames, ))
    screen_listen_th.start()
    send_camera_th.start()
    udp_listen_th.start()
    send_audio_th.start()
    get_audio_th.start()
    app.run(host= '0.0.0.0')