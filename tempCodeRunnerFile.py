@app.route('/facelogin_page')
def facelogin_page():
    global login_status
    print(err_msg)
    if login_status:
        return render_template('index.html')
    return render_template('face_login.html',err_msg=err_msg)