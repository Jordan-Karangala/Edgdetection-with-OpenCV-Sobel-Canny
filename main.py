from PIL import Image
from io import BytesIO
import requests
import os
import shutil
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, URLField
from wtforms.validators import DataRequired, URL
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap5
import cv2

# Initializing Flask application
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'Stinauma@80'
app.config['UPLOAD_FOLDER'] = 'static/uploaded'
# Converting Flask application to bootstrap-flask app
bootstrap = Bootstrap5(app)


# Welcome Form creation
class WelcomeForm(FlaskForm):
    # Option to the user to upload image from local machine or get image from an url
    image_url = BooleanField('Enter image URL')
    upload = BooleanField('Upload')


# Photo/Image upload form
class PhotoForm(FlaskForm):
    photo = FileField(validators=[FileRequired()])
    # submit = SubmitField('Submit')

# URL enter form
class URLInputForm(FlaskForm):
    url = URLField('Enter URL', validators=[DataRequired(), URL(message='Invalid URL')])


#Home route
@app.route('/', methods=['GET','POST'])
def home():

    form = WelcomeForm()
    if request.method == 'POST':
        selected_items = []
        for field in ['image_url', 'web_cam', 'you_tube', 'upload', 'external_cam']:

            if request.form.get(field) == 'y':
                selected_items.append(field)
                print(selected_items)
                if 'image_url' in selected_items:
                    return redirect(url_for('enter_image_url'))
                elif 'upload' in selected_items:
                    return redirect(url_for('upload'))

    return render_template('index.html', form=form)


@app.route('/enter_image_url', methods=['GET','POST'])
def enter_image_url():
    form = URLInputForm()
    if form.validate_on_submit():
        # Retrieve the file
        url = form.url.data
        try:
            # Fetch the image from the URL
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful
            # Validate if the response contains an image
            if "image" not in response.headers["Content-Type"]:
                flash("The URL does not point to an image.", "danger")
                return redirect(url_for('enter_image_url'))
            # Open the image using PIL
            img = Image.open(BytesIO(response.content))

            # Save the image to the upload folder
            image_name = os.path.join('static/uploaded', 'downloaded_image.jpg')
            clear_directory('static/uploaded')
            img.save(image_name)

            flash(f'Image successfully downloaded and saved: {image_name}', 'success')
            edge_detection(image_name)
            return redirect(url_for('edge_detected_image'))

        except requests.exceptions.RequestException as e:
            flash(f'Error fetching image from URL: {str(e)}', 'danger')

    return render_template('image_url.html', form=form)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = PhotoForm()

    if form.validate_on_submit():
        # Retrieve the file
        file = form.photo.data

        # Secure the filename
        filename = secure_filename(file.filename)
        print(filename)
        clear_directory('static/uploaded')
        # Save the file to the configured upload folder
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File uploaded successfully!')
        file_list = os.listdir('static/uploaded')
        file_name = file_list[0]
        file_path = 'static/uploaded/'+file_name
        edge_detection(file_path)
        return redirect(url_for('edge_detected_image'))

    return render_template('upload.html', form = form)

@app.route('/edge_detected_image', methods=['GET', 'POST'])
def edge_detected_image():

    # clear_directory('processed_videos')
    folder_path = 'static/processed/'
    # List all image files in the folder
    images = os.listdir(folder_path)

    return render_template('edges_detected.html', images=images)

def edge_detection(file_path):
    img = cv2.imread(file_path)
    cv2.imwrite('static/processed/Original.jpg', img)

    # Convert to graycsale
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('static/processed/gray_image.jpg', img_gray)

    # Blur the image for better edge detection
    img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)
    cv2.imwrite('static/processed/blur_image.jpg', img_blur)
    # Sobel Edge Detection
    sobelx = cv2.Sobel(src=img_blur, ddepth=cv2.CV_64F, dx=1, dy=0, ksize=5)  # Sobel Edge Detection on the X axis
    cv2.imwrite('static/processed/sobelx_image.jpg', sobelx)
    sobely = cv2.Sobel(src=img_blur, ddepth=cv2.CV_64F, dx=0, dy=1, ksize=5)  # Sobel Edge Detection on the Y axis
    cv2.imwrite('static/processed/sobely_image.jpg', sobely)
    sobelxy = cv2.Sobel(src=img_blur, ddepth=cv2.CV_64F, dx=1, dy=1, ksize=5)  # Combined X and Y Sobel Edge Detection
    cv2.imwrite('static/processed/sobelxy_image.jpg', sobelxy)
    # Canny Edge Detection
    canny_edge = cv2.Canny(image=img_blur, threshold1=100, threshold2=200)  # Canny Edge Detection
    cv2.imwrite('static/processed/canny_edge_image.jpg', canny_edge)
    return

def clear_directory(directory_path):
    if os.path.exists(directory_path):
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')


if __name__ == '__main__':
    app.run(debug=True, port=5000)