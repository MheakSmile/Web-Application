from base64 import encode
import json
import mimetypes
import os
import threading
from datetime import datetime
import time
from tkinter import Frame
from flask import Flask,render_template,request,redirect,Response,url_for,flash,session,jsonify,make_response
from matplotlib.pyplot import text, title
from pyparsing import And
from flask_restful import Api
import mysql.connector
from flask_cors import CORS
import cv2
import subprocess
import argparse

outputFrame = None
lock = threading.Lock()

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY']= "myDetect"
app.config['JSON_AS_ASCII'] = False
CORS(app)
api = Api(app)

url_camera = 'rtsp://admin:aud0821721605@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0'
cap = cv2.VideoCapture(url_camera)
time.sleep(2.0)

host = "192.168.4.2"
user = "sky"
passw = "skyprojectf"
dbname = "project_camera"

conn = mysql.connector.connect(host=host, user=user, password=passw, db=dbname)

@app.route('/')
def index():
    return render_template('login.html',title='Reset Request')

@app.route('/resetpassword')
def resetpassword():
    return render_template('reset_request_id.html',title='Reset Request')

@app.route('/reset_confirm')
def reset_confirm():
    return render_template('reset_password.html',title='Reset Request')

@app.route('/resetpassword/check_validation',methods=['POST'])
def check_validation():
    if request.method=="POST":
        user_id = str(request.form["custId"])
        newpassword = str(request.form["new pass"])
        confirm_newpassword = str(request.form["confirm_new_pass"])

        if newpassword == confirm_newpassword:
            print('matched')
            sql_setpass = (newpassword,user_id)
            cursor = conn.cursor()
            sql = "UPDATE user SET password=%s WHERE user_id=%s"
            cursor.execute(sql,sql_setpass)
            conn.commit()

            return render_template("login.html")
        else:
            msg = 'Passwords did not match'
            return render_template('reset_password.html',title='Reset Request',data=user_id, message=msg)

@app.route('/resetpassword/chk_id',methods=['POST'])
def resetpassword_chk_id():
    msg = ''
    if request.method=="POST":
        username = str(request.form["userid"])
        email = str(request.form["email"])
        sql_user = (username,)
        sql_mail = (email,)
        print(username)
        print(type(username))

        print(email)
        print(type(email))

        cursor1 = conn.cursor()
        cursor2 = conn.cursor()
        
        cursor1.execute("SELECT * FROM user WHERE username = %s",sql_user)
        res1 = cursor1.fetchone()
        
        cursor2.execute("SELECT * FROM user WHERE email = %s",sql_mail)
        res2 = cursor2.fetchone()

        print(res1)
        print(res2)

        if res1 == res2:
            userid = res1[0]
            print(userid)
            return render_template("reset_password.html",data=userid)
        else:
            return render_template("live.html")
    
@app.route('/api/signup' ,methods=['POST'])
def signup():
    mydb = mysql.connector.connect(host=host, user=user, password=passw, db=dbname)
    mycursor = mydb.cursor(dictionary=True)

    # data1 = request.get_json()

    data = request.get_data(as_text=True)
    print(data)
    split1 = data.replace('=','')
    split2 = split1.replace('username','')
    split3 = split2.replace('password','')
    split4 = split3.replace('token','')
    split5 = split4.replace('fullname','')
    split6 = split5.replace('email','')
    split7 = split6.replace('%3A',':')
    split8 = split7.replace('%40','@')
    split9 = split8.replace('+',' ')
    split10 = split9.split("&")

    res = []
    for val in split10:
        if val != '' :
            res.append(val)
            
    db_login = ['fullname','username','password','email','token']
    total = dict(zip(db_login, res))

    print(total)

    _username = total['username']
    _password = total['password']
    _fullname = total['fullname']
    _email = total['email']
    _token = total['token']

    if(_username and _password  and _fullname and _email and _token):
        sql = "INSERT INTO user(username,password,fullname,email,token) value (%s,%s,%s,%s,%s)"
        value = (total['username'], total['password'], total['fullname'], total['email'],total['token'])
        mycursor.execute(sql,value)
        mydb.commit()
        return make_response('Sign Up Success')
    else:   
        return make_response('error')
            
@app.route('/api/login', methods=['POST']) #
def login():
    
    # _json2 = request.get_json()
    _json = request.get_data(as_text=True)

    split1 = _json.replace('=','')
    split12 = split1.replace('username','')
    split13 = split12.replace('password','')
    split14 = split13.replace('token','')
    split5 = split14.split("&")

    res = []
    for val in split5:
        if val != '' :
            res.append(val)
            
    db_login = ['username','password','token']

    total = dict(zip(db_login, res))

    print(total['username'])
    print(total['password'])

    _json1 = request.json

    if(total is not None):
        _username = total['username']
        print(_username)
        _password = total['password']
        mydb = mysql.connector.connect(host=host, user=user, password=passw, db=dbname)
        mycursor = mydb.cursor(dictionary=True)

        sql = "SELECT * FROM user WHERE username=%s AND password=%s"
        sql_where = (_username,_password)

        mycursor.execute(sql, sql_where)
        row = mycursor.fetchone()

        if row:
                mycursor.close()
                return make_response('Login Success')
        else:
                resp = jsonify({'message' : 'Bad Request - invalid password'})
                resp.status_code = 400
                return resp
    else:
        return make_response('NONE !!')

@app.route('/backward')
def backward():
        print('running backward vdo')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vdo")
        rows = cursor.fetchall()
        conn.commit()
        return render_template('backward.html',vdo=rows)

@app.route('/playback_mb')
def playback_mb():
        print('running backward vdo on device')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vdo")
        rows = cursor.fetchall()
        conn.commit()
        return render_template('playbackvideo_mb.html',vdo=rows)

@app.route('/displaybackward')
def displaybackward():
        print('running backward vdo')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vdo")
        rows = cursor.fetchall()
        conn.commit()
        return render_template('playbackvideo_mb.html',vdo=rows)

@app.route('/Login',methods=['POST'])
def adminlogin():
    msg = ''
    admin = None

    cursor = conn.cursor()

    if request.method=="POST":
        username = str(request.form["userid"])
        password = str(request.form["pass"])

        cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s",(username,password))
        user = cursor.fetchone()

        if user != None:
            admin = user[5]
            if admin == 'admin':
                    return render_template("live.html")
            else:
                msg = 'Incorrect user ID or Password !'
                return render_template("login.html", msg = msg)
        else:
            msg = 'Incorrect user ID or Password !'
            return render_template("login.html", msg = msg)

@app.route('/images')
def images():
        print('running')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM images")
        rows = cursor.fetchall()
        conn.commit()
        return render_template('imgMg.html',datas=rows)

@app.route('/displayimages')
def displayimages():
        print('displayimages')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM images")
        rows = cursor.fetchall()
        conn.commit()
        return render_template('displayimage_mb.html',datas=rows)

@app.route('/displayvideo')
def displayvideo():
    print('display video on device')
    return render_template("displayvideo_mb.html")

@app.route("/showdataid")
def showdataid():
        print('display data running')
        # conn1 = mysql.connector.connect("localhost","root","","facedetection")
        cur=conn.cursor()
        cur.execute("SELECT * FROM user")
        rows = cur.fetchall()
        cur.close()
        return render_template('manageID.html',dataid=rows) 

@app.route("/deleteid/<string:id_data>",methods=['GET'])
def deleteid(id_data):
        print('running deteteID')
        print(id_data)
        cur=conn.cursor()
        cur.execute("DELETE FROM user WHERE user_id=%s",[id_data])
        conn.commit() 
        return redirect(url_for('showdataid'))

@app.route('/update',methods=['POST'])
def update():
    if request.method == "POST":
        ID_UPDATE = request.form['id']
        USERNAME = request.form['name']
        PASSWORD = request.form['pass']
        FULLNAME = request.form['fullname']
        EMAIL = request.form['email']
        with conn.cursor() as cursor:
            sql = "update user set username=%s, password=%s, fullname=%s, email=%s where user_id=%s"
            cursor.execute(sql,(USERNAME,PASSWORD,FULLNAME,EMAIL,ID_UPDATE))
            conn.commit()
        return redirect(url_for('showdataid'))

@app.route('/refresh')
def refresh():
    print('refresh images run')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM images")
    rows = cursor.fetchall()
    conn.commit()
    # return render_template('imgMg.html',datas=rows)
    return redirect(url_for('images'))

@app.route('/refreshplayback')
def refreshPlayback():
    print('refresh vdo run')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vdo")
    rows = cursor.fetchall()
    conn.commit()
    # return render_template('imgMg.html',datas=rows)
    return redirect(url_for('backward'))

@app.route('/refreshimages_mb') #******************************* refresh mobile images 
def refreshimages_mb():
    print('refresh images on device run')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM images")
    rows = cursor.fetchall()
    conn.commit()
    # return render_template('imgMg.html',datas=rows)
    return redirect(url_for('displayimages')) #displayimages

@app.route('/refreshvideo_mb') #******************************* refresh mobile video
def refreshvideo_mb():
    print('refresh video run')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vdo")
    rows = cursor.fetchall()
    conn.commit()
    # return render_template('imgMg.html',datas=rows)
    return redirect(url_for('displaybackward'))

@app.route('/live')
def live():
    return render_template("live.html")

def stream(): #frameCount
    global outputFrame, lock
    if cap.isOpened():
        print('cam open')
        while True:
            ret_val, frame = cap.read()
            # print(ret_val)
            if (ret_val is True):
                frame = cv2.resize(frame,(640,400))
                cv2.putText(frame,str(datetime.now().strftime("%d-%m-%Y %H:%M:%S")),(5, 30),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0, 0, 255),2)
                with lock:
                 outputFrame = frame.copy()
            else:
                print('Frame is Empty!!')
                continue
    else:
        print('Failed to open...Check your camera connection')

def generate():
    global outputFrame, lock
    while True:
        with lock:
            if outputFrame is None:
                continue
            (flag, encodedImage) = cv2.imencode(".jpg",outputFrame)
            if not flag:
                continue

        yield(b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n'+ bytearray(encodedImage) + b'\r\n')

def run_detect():
    # os.system("python , save.py")
    print('Detection Running...')
    subprocess.call('python PythonScript\Face_detect.py') #, creationflags=subprocess.CREATE_NO_WINDOW
    time.sleep(2.0)

@app.route('/video_feed')
def video_feed():
    print('Live')
    return Response(generate(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route('/logout')
def logout():
        return redirect(url_for("index"))

if __name__ == "__main__":
    # subprocess.call('python PythonScript\Test.py', creationflags=subprocess.CREATE_NO_WINDOW)
    ap =  argparse.ArgumentParser()
        # ap.add_argument("-i", "--ip", type=str, required=False, default='192.168.1.34', 
        #     help="ip address of the device")                            # 172.20.10.14
        # ap.add_argument("-o", "--port", type=int, required=False, default=5000, 
        #     help="ephemeral port number of the server (1024 to 65535)")
    # ap.add_argument("-f", "--frame-count", type=int, default=32,
    #         help="# of frames used to construct the background model")
    args = vars(ap.parse_args())

    t = threading.Thread(target=stream) #, args=(args["frame_count"],)
    t1 = threading.Thread(target=run_detect)
    t.daemon = True
    t1.daemon = True
    t.start()
    t1.start()

    # app.run(debug=True, use_reloader=False, threaded=True) # host=args["ip"], port=args["port"], , host='0.0.0.0', port=8080 debug=True,
    app.run(debug=True, use_reloader=False, threaded=True,host='192.168.4.2', port=5001) # host=args["ip"], port=args["port"], , host='0.0.0.0', port=8080
 