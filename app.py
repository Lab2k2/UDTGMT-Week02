from flask import Flask, render_template, request, Response, redirect, url_for
import cv2
import face_recognition
import numpy as np
import os
import base64
from controller import ImageController
app = Flask(__name__,template_folder='template')
app.config['UPLOAD_FOLDER'] = 'uploads'
err_msg=""
# Biến lưu trạng thái đăng nhập
login_status = False

# Biến lưu trữ hình ảnh từ máy ảnh
camera = cv2.VideoCapture(0)

# Hàm để truyền video từ máy ảnh vào trang web
def generate_frames():
    while True:
        success, frame = camera.read()  # Đọc frame từ máy ảnh
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def login_page():
    global login_status
    if login_status:
        return redirect(url_for('index'))
    return render_template('login.html',err_msg=err_msg)
@app.route('/facelogin_page')
def facelogin_page():
    global login_status
    if login_status:
        return redirect(url_for('index'))
    return render_template('face_login.html',err_msg=err_msg)
@app.route('/index')
def index():
    global login_status
    if login_status:
        return render_template('index.html')
    return redirect(url_for('login_page'))

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/login', methods=['POST'])
def login():
    global login_status
    global err_msg
    err_msg=""
    if request.method == 'POST':
        username = request.form['user_name']
        password = request.form['pass_word']
        val=ImageController.user_validate(username,password)
        print(val)
        if True == val:
            login_status = True
            return redirect(url_for('index'))
        else: err_msg="DANG NHAP THAT BAI"
    return redirect(url_for('login_page'))
@app.route('/face_login', methods=['POST'])
def face_login():
    global login_status
    global err_msg
    err_msg=""
    # Đọc hình ảnh từ video
    success, frame = camera.read()
    if success:
        username = request.form['user_name']
        matche=ImageController.facelogin_validate(username,frame)
        if True in matche:
            login_status = True
            return redirect(url_for('index'))
        else: err_msg="DANG NHAP THAT BAI"
    return redirect(url_for('facelogin_page'))
@app.route('/logout', methods=['POST'])
def logout():
    global login_status
    login_status = False
    return redirect(url_for('login_page'))
@app.route('/register', methods=['GET', 'POST'])
def register():
    global login_status
    global err_msg
    err_msg=""
    if request.method == 'POST':
        user_name = request.form['user_name']
        pass_word = request.form['pass_word']
        if 'user_image' in request.files:
            user_image = request.files['user_image']
            user_image_path = os.path.join('static/image', user_name + '.jpg')
            user_image.save(user_image_path)
            ImageController.add_user(user_name,pass_word,user_image_path)
            err_msg= "Registration successful!"
            return render_template('register.html',err_msg=err_msg)
    return render_template('register.html')
@app.route("/upload", methods=["GET", "POST"])
def upload():
    global login_status
    if login_status:
        if request.method == "POST":
            file = request.files["image"]
            if file:
                img_controller = ImageController(app.config['UPLOAD_FOLDER'])
                img_path = img_controller.upload_image(file)
                gray_image = img_controller.convert_to_gray(img_path)
                _, buffer = cv2.imencode('.jpg', gray_image)
                image_bytes = base64.b64encode(buffer.tobytes()).decode('utf-8')
                return render_template("result.html", image_bytes=image_bytes)
            
        return render_template("upload.html")
    else:
        return redirect(url_for('login_page'))
@app.route("/fdetect", methods=["GET", "POST"])
def fdetect():
    global login_status
    if login_status:
        if request.method == "POST":
            file = request.files["image"]
            if file:
                img_controller = ImageController(app.config['UPLOAD_FOLDER'])
                img_path = img_controller.upload_image(file)
                fd_image =img_controller.fdetect(img_path)
                _, buffer = cv2.imencode('.jpg', fd_image)
                image_bytes = base64.b64encode(buffer.tobytes()).decode('utf-8')
                return render_template("result.html", image_bytes=image_bytes)
            
        return render_template("fdetect.html")
    else:
        return redirect(url_for('login_page'))
if __name__ == '__main__':
    app.run(debug=True)

