from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image, ImageEnhance
from io import BytesIO

app = Flask(__name__, template_folder='template')
app.config['UPLOAD_FOLDER'] = 'static/uploads'

def adjust_brightness(image, factor):
    enhancer = ImageEnhance.Brightness(image)
    enhanced_image = enhancer.enhance(factor)
    return enhanced_image
def crop_img(image,a,b):
    return 0
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return render_template('index.html', error='No file part')

    file = request.files['file']

    if file.filename == '':
        return render_template('index.html', error='No selected file')

    if file:
        filename = 'original.jpg'
        filepath = f"{app.config['UPLOAD_FOLDER']}/{filename}"
        file.save(filepath)

        return render_template('index.html', filename=filename)

@app.route('/process/<filename>', methods=['POST'])
def process(filename):
    factor = float(request.form['brightness'])
    filepath = f"{app.config['UPLOAD_FOLDER']}/{filename}"

    image = Image.open(filepath)
    enhanced_image = adjust_brightness(image, factor)

    output = BytesIO()
    enhanced_image.save(output, format='JPEG')
    output.seek(0)

    return send_file(output, as_attachment=True, download_name='enhanced.jpg', mimetype='image/jpeg')
@app.route('/crop/<filename>', methods=['POST'])
def crop(filename):
    factor = float(request.form['crop'])
    filepath = f"{app.config['UPLOAD_FOLDER']}/{filename}"

    image = Image.open(filepath)
    enhanced_image = crop_img(image, factor)

    output = BytesIO()
    enhanced_image.save(output, format='JPEG')
    output.seek(0)

    return send_file(output, as_attachment=True, download_name='enhanced.jpg', mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)
