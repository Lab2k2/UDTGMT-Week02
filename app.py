from controller import ImageController
import cv2
import base64
from flask import Flask, render_template, request, redirect, url_for, flash
app = Flask(__name__,template_folder='template')
app.config['UPLOAD_FOLDER'] = 'uploads'

    
@app.route("/", methods=["GET", "POST"])
def login():
    err_msgs=""
    if request.method == 'POST':
        usernames = request.form['username']
        passwords = request.form['password']
        user = ImageController.validate_user(usernames,passwords)
        if user:
            return redirect(url_for("index"))
        else:
            err_msgs="DANG NHAP THAT BAI"
    return render_template('login.html',err_msg=err_msgs)
@app.route("/register", methods=["GET", "POST"])
def register():
    err_msgs=""
    if request.method == 'POST':
        usernames = request.form['username']
        passwords = request.form['password']
        user = ImageController.user_exists(usernames)
        if user:
            err_msgs="TAI KHOAN DA TON TAI"
        else:
            err_msgs="DANG KI THANH CONG"
            ImageController.add_user(username=usernames,password=passwords)
    return render_template('register.html',err_msg=err_msgs)
@app.route("/index", methods=["GET", "POST"])
def index():
    return render_template("index.html")
@app.route("/upload", methods=["GET", "POST"])
def upload():
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
@app.route("/fdetect", methods=["GET", "POST"])
def fdetect():
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

if __name__ == "__main__":
    app.run(debug=True)

