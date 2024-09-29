# import cv2
# import matplotlib.pyplot as plt
# import requests
import os
from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, SelectField, FileField
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap5
import cv2



app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'Stinauma@80'
app.config['UPLOAD_FOLDER'] = 'static/uploaded'

bootstrap = Bootstrap5(app)
class WelcomeForm(FlaskForm):
    image_url = BooleanField('Enter image URL')
    web_cam = BooleanField('Live Stream')
    you_tube = BooleanField('You_tube_url')
    upload = BooleanField('Upload')
    external_cam = BooleanField("Ext_Camera")
    # submit = SubmitField('Submit')


class PhotoForm(FlaskForm):
    photo = FileField(validators=[FileRequired()])
    # submit = SubmitField('Submit')

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
                    source = 'downloaded_videos/downloaded_video.mp4'
                    # camera_choices.append(source)
                    return redirect(url_for('you_tube_url'))
                elif 'web_cam' in selected_items:
                    source = 0
                    # camera_choices.append(source)
                    return redirect(url_for('web_cam_track'))
                elif 'external_cam' in selected_items:
                    # Check for additional connected cameras
                    for i in range(1, 5):  # Check first 5 camera indices (expand range if needed)
                        cap = cv2.VideoCapture(i)
                        # if cap.isOpened():
                            # camera_choices.append((str(i), f'External Camera {i}'))
                        cap.release()
                    # camera_choices.append(source)
                    return redirect(url_for('select_camera'))
                # if 'test_data' in selected_items:
                #     car_models_df = pd.read_csv('data files/Car+names+and+make.csv')
                #     car_models_list = car_models_df['AM General Hummer SUV 2000'].to_list()
                #     return redirect(url_for('select_pics'))
                elif 'desktop' in selected_items:

                    return redirect(url_for('upload'))
                elif 'upload' in selected_items:
                    return redirect(url_for('upload'))

    return render_template('index.html', form=form)



@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = PhotoForm()

    if form.validate_on_submit():
        # Retrieve the file
        file = form.photo.data

        # Secure the filename
        filename = secure_filename(file.filename)
        print(filename)
        # Save the file to the configured upload folder
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        flash('File uploaded successfully!')
        return redirect(url_for('edge_detected_image'))

    return render_template('upload.html', form = form)

@app.route('/edge_detected_image', methods=['GET', 'POST'])
def edge_detected_image():

    # clear_directory('processed_videos')
    file_name = os.listdir('static/uploaded')
    file_path = os.path.join('static/uploaded', file_name[0])
    print(file_path)
    edge_detection(file_path)
    # Folder where the processed images are saved
    folder_path = 'static/processed/'

    # List all image files in the folder
    images = os.listdir(folder_path)

    return render_template('edges_detected.html', images=images)

def edge_detection(filepath):
    img = cv2.imread(filepath)

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)