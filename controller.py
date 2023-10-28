import os
import cv2
import uuid
import json
from flask import Flask
import hashlib
import face_recognition
app = Flask(__name__)
def read_user():
    with open(os.path.join(app.root_path,"data/user.json"),
            encoding="utf-8") as f:
            data=json.load(f)
    return data
class ImageController:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        self.create_upload_folder()

    def create_upload_folder(self):
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)

    def upload_image(self, file):
        if file:
            file_extension = file.filename.split(".")[-1]
            unique_filename = str(uuid.uuid4()) + "." + file_extension
            image_path = os.path.join(self.upload_folder, unique_filename)
            file.save(image_path)
            return image_path

    def convert_to_gray(self, image_path):
        image = cv2.imread(image_path)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_image_path = os.path.join(self.upload_folder, "gray_" + os.path.basename(image_path))
        cv2.imwrite(gray_image_path, gray_image)
        return gray_image
    
    def fdetect(self, image_path):
        image = cv2.imread(image_path)
        gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces=face_classifier.detectMultiScale(gray,1.1,5)
        if faces is (False):
            return image
        for (x,y,w,h) in faces:
            cv2.rectangle(image,(x,y),(x+w,y+h),(127,255,0),2)
        fd_image_path = os.path.join(self.upload_folder, "fd_" + os.path.basename(image_path))
        cv2.imwrite(fd_image_path, image)
        return image
        
    def user_validate(username,password):
        users=read_user()
        password=str(hashlib.md5(password.strip().encode("utf-8")).hexdigest())
        for user in users:
            if user["username"].strip() == username.strip() and user["password"].strip()==password.strip():
                return True
        return False
    def face_validate(frame):
        users=read_user()
        user_face_encodings = []
        for user in users:
            registered_face = face_recognition.load_image_file(user["image_path"])
            registered_face_encoding = face_recognition.face_encodings(registered_face)[0]
            user_face_encodings.append(registered_face_encoding)
        face_locations = face_recognition.face_locations(frame)
        if face_locations:
            face_encoding = face_recognition.face_encodings(frame, face_locations)[0]
            matches = face_recognition.compare_faces(user_face_encodings, face_encoding)
        return matches
    def facelogin_validate(username,frame):
        users=read_user()
        matches=[]
        user_face_encodings = []
        for user in users:
            user_name=user["username"]
            if user_name==username:
                registered_face = face_recognition.load_image_file(user["image_path"])
                registered_face_encoding = face_recognition.face_encodings(registered_face)[0]
                user_face_encodings.append(registered_face_encoding)
                #Anh duoc chụp tu camera
                face_locations = face_recognition.face_locations(frame)
                if face_locations:
                    face_encoding = face_recognition.face_encodings(frame, face_locations)[0]
                    matches = face_recognition.compare_faces(user_face_encodings, face_encoding)
        return matches
    def user_exists(username):
        users=read_user()
        for user in users:
            if user["username"].strip() == username.strip():
                return user
        return None
    def add_user(username,password,path):
        users=read_user()
        user = {
            "id": len(users)+1,
            "username":username.strip(),
            "password":str(hashlib.md5(password.strip().encode("utf-8")).hexdigest()),
            "image_path":path.strip()
        }
        print(users)
        users.append(user)
        with open(os.path.join(app.root_path,"data/user.json"),"w",encoding="utf-8") as f:
            json.dump(users,f,ensure_ascii=False,indent=4)
        return user
