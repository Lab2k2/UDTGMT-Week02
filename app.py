from flask import Flask, render_template, request, Response, redirect, url_for,send_file, jsonify
import cv2
import face_recognition
import numpy as np
import os
import base64
from controller import ImageController
from PIL import Image, ImageEnhance
from io import BytesIO
import Unblurred
import fastSrgan

app = Flask(__name__,template_folder='template',static_folder='static')
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
    if 'image' in request.form:
        image_file = request.form['image']
        image=ImageController.change64toimg(image_file)
        if image_file != '':
            username = request.form['username']
            print(username)
        matche=ImageController.facelogin_validate(username,image)
        print(matche)
        if True in matche:
            print(0)
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
@app.route('/upload', methods=['POST'])
def upload():
    global login_status
    if login_status:
            file = request.files['file']
            if file:
                img_data = file.read()
                img_str = base64.b64encode(img_data).decode('utf-8')
                return jsonify({'image': img_str})
            return jsonify({'error': 'No file uploaded'})
    else:
        return redirect(url_for('login_page'))
@app.route('/convert_to_gray', methods=['POST'])
def convert_to_gray():
    img_data = request.json.get('image')  # Nhận dữ liệu ảnh từ client
    img_data = base64.b64decode(img_data)  # Giải mã dữ liệu ảnh từ base64
    nparr = np.frombuffer(img_data, np.uint8)  # Chuyển đổi thành mảng numpy
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # Đọc ảnh từ mảng numpy
    
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Chuyển đổi ảnh sang ảnh xám

    # Chuyển lại ảnh xám thành dạng base64 để gửi về client
    _, buffer = cv2.imencode('.jpg', gray_img)
    gray_img_str = base64.b64encode(buffer).decode('utf-8')

    return jsonify({'image': gray_img_str})
@app.route('/image_restored', methods=['POST'])
def image_restored():
    img_data = request.json.get('image')  # Nhận dữ liệu ảnh từ client
    img_data = base64.b64decode(img_data)  # Giải mã dữ liệu ảnh từ base64
    dir_in='test.jpg'
    dir_out='submit/test.jpg'
    with open(dir_in, 'wb') as file:
        file.write(img_data)
    
    Unblurred.debulr(dir_in)
    with open(dir_out, "rb") as file:
        new_img = file.read()
        img_str = base64.b64encode(new_img).decode('utf-8')
    return jsonify({'image': img_str})
@app.route('/image_enhance', methods=['POST'])
def image_enhance():
    img_data = request.json.get('image')  # Nhận dữ liệu ảnh từ client
    img_data = base64.b64decode(img_data)  # Giải mã dữ liệu ảnh từ base64
    dir_in='test.jpg'
    dir_out='submit/test.jpg'
    with open(dir_in, 'wb') as file:
        file.write(img_data)
    
    fastSrgan.srgan(dir_in)
    with open(dir_out, "rb") as file:
        new_img = file.read()
        img_str = base64.b64encode(new_img).decode('utf-8')
    return jsonify({'image': img_str})

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

