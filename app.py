from flask import Flask,flash, render_template, request, redirect, url_for,jsonify
from flask_mysqldb import MySQL
from flask_session import Session
from sqlalchemy import create_engine
import json
import os
import hashlib 
import jwt
import urllib.request
from werkzeug.utils import secure_filename
from flask import abort
from flask import session
from datetime import datetime, timedelta
import secrets
import string
from moviepy.editor import ImageClip, concatenate_videoclips,vfx,VideoFileClip
from moviepy.editor import concatenate_audioclips
from PIL import Image
from io import BytesIO
import numpy as np
from flask import send_file
import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from moviepy.audio.AudioClip import AudioArrayClip
from moviepy.editor import AudioFileClip
from moviepy.editor import VideoFileClip, CompositeVideoClip
from moviepy.video.fx import fadein
from moviepy.video.fx import fadeout
from moviepy.video import fx
from moviepy.video.fx import all as vfx
import shutil
from pathlib import Path
import base64
from collections import defaultdict
from datetime import date
from moviepy.editor import ImageSequenceClip
import subprocess
import tempfile
from functools import reduce

import numpy as np

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.VideoClip import ColorClip, VideoClip



db_url = "postgresql://aditya:DZAx1bXrFJrZLaGcyEtJOQ@early-faerie-8845.8nk.gcp-asia-southeast1.cockroachlabs.cloud:26257/iss_project_t1?sslmode=verify-full&sslrootcert=root.crt"
conn = psycopg2.connect(db_url)

app = Flask(__name__)
def hash_password(password):
  
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

UPLOAD_FOLDER = 'static/uploads/'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
# app.config['SESSION_TYPE'] = 'filesystem'

 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
     

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'MySql@123'
app.config['MYSQL_DB'] = 'iss_project_t1'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

secret_key = "swampandi"
secret_key=hash_password(secret_key)
app.config['SECRET_KEY'] = secret_key

mysql = MySQL(app)

global temp_user



# @app.before_request
# def clear_token():
#     # Clear the existing token from the session
#     session.pop('token', None)


@app.route('/signuppage', methods=['GET', 'POST'])
def signuppage():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['pwd']
        cpassword = request.form['cpwd']
        name = request.form['name']
        dob = request.form['dob']
        security_question = request.form['security_question']
        security_ans = request.form['security_ans']

       # Check if user already exists
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cur.fetchone()
        cur.close()
        if existing_user:
            # User already exists, display alert message
            alert_message = "User '{}' already exists.".format(username)
            return render_template('signupage.html', alert_message=alert_message)
        else:
           
            pass

      
        password=hash_password(password)
        cur = conn.cursor()
        cur.execute("INSERT INTO users(name, dob, username, password, security_question, security_ans) VALUES (%s, %s, %s, %s, %s, %s)", (name, dob, username, password, security_question, security_ans))
        conn.commit()
        cur.close()


        return redirect(url_for('login')) 

    return render_template('signupage.html')


def generate_jwt_token(username):
   # payload = {'username': username,'exp': datetime.utcnow() + timedelta(hours=1)}
    secret_key = app.config['SECRET_KEY'].encode('utf-8')  # Encode secret key as bytes
    token = jwt.encode( {'username': username,'exp': datetime.utcnow() + timedelta(hours=1)}, secret_key, algorithm='HS256')
    return token


@app.route('/',methods=['GET','POST'])
def index():
    global temp_user
    if 'username' in session:
        temp_user = session['username']
    else:
        temp_user = 'admin'
    return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
       token = None
       username = request.form.get('username')
       password = request.form.get('password')
       password=hash_password(password)

       cur = conn.cursor()
       cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
       user = cur.fetchone()
       cur.close()
    

       if user:
            token = generate_jwt_token(username)
            session['token'] = token
            session['username'] = username
            return redirect(url_for('user_homepage',token=token))
       else:
           alert_message = "wrong username or password"
           return render_template('login_page.html', alert_message=alert_message)
           
    print('hello')
   
    token = session.get('token')
    if not token:
        print('missing')
        return render_template('login_page.html')  # Redirect to login page if token is missing
    
    try:
        print('valid')
        decoded_token = jwt.decode(token,app.config['SECRET_KEY'] , algorithms=['HS256'])
        # Validate token claims, expiration, etc. here

        if decoded_token['username']:
            print("valid-1")
            return redirect(url_for('user_homepage', token=token))  # Fix here
        else:
            print('invalid-2')
            session.pop('token', None)
            return render_template('login_page.html')
    except jwt.ExpiredSignatureError:
        print('expiry')
        session.pop('token', None)
        return render_template('login_page.html')
    except jwt.InvalidTokenError:
        print('invalid-jwt')
        session.pop('token', None)
        return render_template('login_page.html')

    return render_template('login_page.html')


@app.route('/logout')
def logout():
    # Remove the token from the session
    session.pop('token', None)
    session.pop('username',None)
    return redirect(url_for('index'))


@app.route('/forgetpage',methods=['GET','POST'])
def forgetpage():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('pwd')
        cpassword = request.form.get('cpwd')
        dob = request.form.get('DOB')
        security_question = request.form.get('security_question')
        security_ans = request.form.get('security_ans')

        password = hash_password(password)
        # print(f"Checking for user: {username}")

        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s and dob = %s and security_question = %s and security_ans = %s", (username, dob, security_question, security_ans))
        user = cur.fetchone()

        if user:
            # User found, update the password in the database
            # Assuming cpassword is the new password
            cur.execute("UPDATE users SET password = %s WHERE username = %s", (password, username))
            conn.commit()
            cur.close()

            alert_message = "Password changed successfully"
            #print(f"User found: {username}")
            return render_template('forgetpage.html', alert_message=alert_message)
        else:
            cur.close()
            alert_message = "User not found"
            # print(f"User not found: {username}")
            return render_template('forgetpage.html', alert_message=alert_message)

    return render_template('forgetpage.html')

@app.route('/user_homepage/<token>', methods=['GET', 'POST'])
def user_homepage(token):
    global temp_user
    if 'username' in session:
        temp_user = session['username']
    else:
        temp_user = 'admin'
        return redirect(url_for('login'))
    

    decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    username = decoded_token['username']
    
  
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    

    if not user:
        abort(404)


    user_data = {
        'username': user[3],
        'name': user[1],
        'dob':user[2],
        'user_id':user[0],

    }
    temp_user = user[3]

    cur.execute("SELECT image_blob FROM profile_pic WHERE username = %s", (temp_user,))
    profile_pic_data = cur.fetchone()
    profile_pic = None
    if profile_pic_data:
        print("helloji")
        profile_pic = base64.b64encode(profile_pic_data[0]).decode('utf-8')
    else:
        print("yo")
        with open("static/images/pfp.avif", 'rb') as f:
            profile_pic = base64.b64encode(f.read()).decode('utf-8')


    grouped_images = defaultdict(list) 
    cur.execute("SELECT image_blob, date FROM image_data WHERE username = %s ORDER BY date DESC", (temp_user,))
    images_data = cur.fetchall()
    cur.close()


    for image_blob, date in images_data:
        grouped_images[date].append(base64.b64encode(image_blob).decode('utf-8'))

    grouped_images = dict(grouped_images)
    print(len(profile_pic))
    print(profile_pic[:20])

    return render_template("user_homepage.html", user_data=user_data, grouped_images=grouped_images,profile_pic=profile_pic)




@app.route('/view_slideshow',methods=['GET','POST'])
def view_slideshow():
    if request.method == 'GET':
        # Fetch video paths for the current user (temp_user)
        cur = conn.cursor()
        cur.execute("SELECT video_path FROM videos WHERE username = %s", (temp_user,))
        video_paths = [row[0] for row in cur.fetchall()]
        cur.close()
        video_names = [os.path.basename(video_path) for video_path in video_paths]

        video_info = list(zip(video_names, video_paths))

        return render_template("view_slideshow.html", temp_user=temp_user, video_info=video_info)


    return render_template("view_slideshow.html",temp_user =temp_user)



def retrieve_images_from_db(selected_images):
    try:
        connection = conn.cursor()
        images_data = []
        # Iterate through selected_images list
        for filename in selected_images:
            # Prepare a parameterized query to select image data for each filename
            query = "SELECT filename, image_blob FROM image_data WHERE filename = %s"
            # Execute the query for the current filename
            connection.execute(query, (filename,))
            # Fetch the image data and append to images_data list
            image_data = connection.fetchone()
            if image_data:
                images_data.append(image_data)
        print("Retrieved images:", images_data)
        return images_data
    except Exception as e:
        print("Error retrieving images:", e)
        return None
    finally:
        if connection:
            connection.close()


def insert_video_info(username, video_path):
    try:
        cur = conn.cursor()
        video_path = str(video_path)
        cur.execute("INSERT INTO videos (username, video_path) VALUES (%s, %s)", (username, video_path))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print("Error inserting video info:", e)
        return False


def move_file(source_path, destination_directory, username):
    source_path = Path(source_path)
    destination_directory = Path(destination_directory)

    destination_path = destination_directory / f"{username}_{source_path.name}"

    # Generate a unique filename if the file already exists in the destination directory
    while destination_path.exists():
        base_name, extension = os.path.splitext(destination_path.name)
        destination_path = destination_directory / f"{base_name}_new{extension}"

    # Move the file
    os.rename(source_path, destination_path)

    return destination_path

def resize_image(image_data, target_size):
    image = Image.open(BytesIO(image_data))
    image = image.resize(target_size)
    buffered = BytesIO()
    image = image.convert("RGB")  # Convert image to RGB mode before saving as JPEG
    image.save(buffered, format="JPEG")
    return buffered.getvalue()

def apply_transition(image1_data, image2_data,resolution_width, resolution_height, transition='fade', duration=2, offset=0.5):
    # Write image data to temporary files
    target_size = (resolution_width, resolution_height)  # Set target size
    image1_data = resize_image(image1_data, target_size)
    image2_data = resize_image(image2_data, target_size)
    
    with BytesIO(image1_data) as f1, BytesIO(image2_data) as f2:
        print("debug-1")
        # Set up temporary file names
        temp_image1 = 'temp_image1.jpg'
        temp_image2 = 'temp_image2.jpg'
        print("debug-2")
        # Save images to temporary files
        with open(temp_image1, 'wb') as img_file1, open(temp_image2, 'wb') as img_file2:
            print("debug-3")
            img_file1.write(f1.read())
            img_file2.write(f2.read())
            print("debug-4")
        
        # FFmpeg command to create transition video
        command = [
            r"C:\Users\adity\Downloads\ffmpeg-6.1.1-full_build\ffmpeg-6.1.1-full_build\bin\ffmpeg.exe",
            '-loop', '1', '-i', temp_image1,  # Loop input image1 indefinitely
            '-loop', '1', '-i', temp_image2,  # Loop input image2 indefinitely
            '-filter_complex', f'[0:v]scale=1920:1080[v0];[1:v]scale=1920:1080[v1];'
                            f'[v0]fade=out:st={duration}:d={duration}[fadeOut];'
                            f'[v1]fade=in:st=0:d={duration}[fadeIn];'
                            f'[0:v][fadeOut]overlay[fadedOut];'
                            f'[1:v][fadeIn]overlay[fadedIn];'
                            f'[fadedOut][fadedIn]xfade=transition={transition}:duration={duration}:offset={offset}[outv]',
            '-map', '[outv]',  # Map the output of the filter graph
            '-c:v', 'libx264',  # Video codec
            '-pix_fmt', 'yuv420p',  # Pixel format
            '-t', '1',  # Duration of the resulting transition video (1 second)
            '-y',
            'transition_clip.mp4',  # Output file path
        ]

        
        # Run FFmpeg command and capture sstdout
        print("debug-5")
        result = subprocess.run(command, capture_output=True)
        print("debug-6")

        # Clean up temporary files
        try:
            print("debug-7")
            os.remove(temp_image1)
            print("debug-8")
            os.remove(temp_image2)
            print("debug-9")
        except FileNotFoundError:
            print("debug-10")
            pass

        if result.returncode == 0:
            print("debug-11")
            # Return transition video clip data
            # return result.stdout
        else:
            print("Error creating transition video:", result.stderr)
            return None

    
def create_transitioned_clip(clip1, clip2, transition_effect='pixelize'):
    transition_duration = 1  # Transition duration in seconds
    transition_offset = 3  # Transition offset in seconds





def convert_to_image_clip(transition_clip_path, duration):
    # Load the video clip
    video_clip = VideoFileClip(transition_clip_path)

    # Convert the video clip to an image clip
    transition_clip = video_clip.to_ImageClip(t=duration)

    # Close the video clip
    video_clip.close()

    return transition_clip

@app.route('/create_slideshow', methods=['GET', 'POST'])
def create_slideshow():
    global temp_user
    if 'username' in session:
        temp_user = session['username']
    else:
        temp_user = 'admin'
    if request.method == 'POST':
        
        number_of_images = int(request.form['number_of_images'])
        video_name = request.form['video_name']
        video_name+=".mp4"
        selected_images = request.form.getlist('selected_images')
        image_durations = [int(duration) for duration in request.form.getlist('imageDurations[]')]
        background_music = request.form.getlist('backgroundMusic')
        transition_effects = request.form.getlist('transitionEffect')
        resolution = request.form.get('resolution')

        print("video-name",video_name)
        print("Number of Images:", number_of_images)
        print("Selected Images:", selected_images)
        print("Image Durations:", image_durations)
        print("Background Music:", background_music)
        print("Transition Effects:", transition_effects)


        dicn1={
            "Nostalgia":"audio1.mpeg","Memories":"audio2.mpeg","Bhaijaan":"audio3.mpeg","Dusk":"audio4.mpeg"
        }
        resolution_mapping = {
            "360p": (480, 360),
            "720p": (1280, 720),
            "1080p": (1920, 1080)
        }

        resolution_width, resolution_height = resolution_mapping.get(resolution, (1280, 720))

        for i in range(len(background_music)):
            background_music[i]= dicn1[background_music[i]]

        
        images_data = retrieve_images_from_db(selected_images)
        
        clips = []
        for i, (filename, image_blob) in enumerate(images_data):
            with BytesIO(image_blob) as f:
                img = Image.open(f)
                img_clip = ImageClip(np.array(img)).set_duration(image_durations[i])  

                if i > 0 and i < len(transition_effects):
                    transition = transition_effects[i]
                    if transition == "fade-in":
                        # if i < len(images_data):
                        #     current_image_data = images_data[i-1][1]
                        #     next_image_data = images_data[i][1]
                            
                        #     apply_transition(current_image_data,next_image_data,transition="fade",resolution_width=resolution_width,resolution_height= resolution_height)

                        #     transition_clip = convert_to_image_clip("transition_clip.mp4", duration=2)

                        #     transition_clip = transition_clip.set_duration(2)   
                        #     clips.append(transition_clip)
                        fadein_duration = 2
                        img_clip = img_clip.fadein(fadein_duration)

                    elif transition == "fade-out":
                        fadeout_duration = 2  # Set your desired fade-out duration
                        img_clip = img_clip.fadeout(fadeout_duration)
                    elif transition == "crossfade-in":
                        crossfade_duration = 2
                        img_clip = img_clip.crossfadein(crossfade_duration)
                    elif transition == "crossfade-out":
                        crossfade_duration = 2
                        img_clip = img_clip.fadeout(crossfade_duration)
                    elif transition == "fade-in-fade-out":
                        fadein_duration = 1
                        fadeout_duration = 1
                        img_clip = img_clip.fadein(fadein_duration).fadeout(fadeout_duration)
                    elif transition == "none":
                        pass
                
                if i < len(background_music):
                    music_file = 'static/audio_files/' + background_music[i]  
                    audio_clip = AudioFileClip(music_file)
                    audio_clip = audio_clip.set_duration(image_durations[i])  
                    img_clip = img_clip.set_audio(audio_clip)

                clips.append(img_clip)
        for idx, clip in enumerate(clips):
            print(f"Clip {idx}: {clip.duration} seconds")
      
        print(clips,'clips')
        video_clip = concatenate_videoclips(clips, method='compose').resize((resolution_width, resolution_height))
        video_filename = video_name
        video_clip.write_videofile(video_filename, fps=24, remove_temp=True, codec="libx264", audio_codec="aac")
        video_static_path = os.path.join('static', 'video_files', video_name)


        video_static_path = move_file(video_name, os.path.join('static', 'video_files'),temp_user)
        insert_success = insert_video_info(username=temp_user, video_path=video_static_path)
        if insert_success:
            print("insert success")

        cur = conn.cursor()
        cur.execute(f"SELECT filename FROM image_data where username ='{temp_user}'")
        all_images = [row[0] for row in cur.fetchall()]
        all_images = list(set(all_images))
        cur.close()
        print(video_static_path)

        return render_template("create_slideshow.html",token=session['token'], all_images=all_images,video_name=video_name,video_static_path=video_static_path, video_url=url_for('static', filename=f'video_files/{video_name}'))
    


    cur = conn.cursor()
    cur.execute(f"SELECT filename FROM image_data where username ='{temp_user}'")
    all_images = [row[0] for row in cur.fetchall()]
    all_images = list(set(all_images))
    cur.close()

    return render_template("create_slideshow.html",token=session['token'], all_images=all_images)


@app.route('/change_password',methods=['GET','POST'])
def change_password():
    return render_template("change_password.html")

@app.route('/delete_account',methods=['GET','POST'])
def delete_account():
    # if request.method == 'POST':
    #     token = session.get('token')
    #     if not token:
    #         return redirect(url_for('login'))
        
    #     try:
    #         decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    #         username = decoded_token['username']
    #     except jwt.ExpiredSignatureError:
    #         return redirect(url_for('login'))
    #     except jwt.InvalidTokenError:
    #         return redirect(url_for('login'))

    #     password = request.form.get('password')
    #     password = hash_password(password)

    #     cur = conn.cursor()
    #     cur.execute = ("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    #     user = cur.fetchone()
    #     cur.close()

    #     if user:
    #         cur = conn.cursor()
    #         cur.execute = ("DELETE FROM users WHERE username = %s AND password = %s", (username, password))
    #         conn.commit()
    #         cur.close()
    #         return redirect(url_for(''))
    #     elif user[3] != username or user[4] != password:
    #         alert_message = "Entered incorrect username or password! Try again!"
    #         return render_template('delete_account.html', alert_message=alert_message)
            
    return render_template('delete_account.html')


@app.route('/upload_image')
def home():
    return render_template('upload_image.html',token = session['token'])

@app.route('/upload_image',methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    files = request.files.getlist('file')
    filenames = []
    cur = conn.cursor()
    for file in files:
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        file_stream = BytesIO()
        file.save(file_stream)
        file_stream.seek(0)
        image_data = file_stream.read()
        try:
            img = Image.open(BytesIO(image_data))

            
            filename = file.filename
            filenames.append(filename)
            width, height = img.size
            img_format = img.format
            img_mode = img.mode
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO image_data (filename, width, height, format, mode, image_blob, username) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (filename, width, height, img_format, img_mode, image_data, temp_user))
            conn.commit()
        except Exception as e:
            return f'Error: {str(e)}', 500  
    cur.close()

    flash('Images successfully uploaded and displayed below')
    return redirect(url_for('display_images',token=session['token'] ,filenames=filenames))
 
@app.route('/upload_image/display', methods=['GET'])
def display_images():
    filenames = request.args.getlist('filenames')
    print(filenames)
    print(len(filenames))
    cur = conn.cursor()
    images = []
    for filename in filenames:
        cur.execute("SELECT image_blob FROM image_data WHERE username = %s AND filename = %s", (temp_user, filename))
        image_data = cur.fetchone()
        if image_data:
           decoded_image = base64.b64encode(image_data[0]).decode('utf-8')
           images.append(decoded_image) 
    cur.close()

    return render_template('upload_image.html',images=images,token = session['token'])


    # try:
    #     cur = conn.cursor()
    #     for filename in filenames:
    #         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    #         with Image.open(file_path) as img:
    #             width, height = img.size
    #             format = img.format
    #             mode = img.mode

    #             with open(file_path, 'rb') as f:
    #                 image_data = f.read()
    #                 cur.execute("INSERT INTO image_data (filename, width, height, format, mode, image_blob, username) VALUES (%s, %s, %s, %s, %s, %s, %s)", (filename,width,height,format,mode,image_data,temp_user))
    #                 conn.commit()
    #     cur.close()

    #     return render_template('upload_image.html', filenames=filenames,token = session['token'])
    # except Exception as e:
    #     flash(f'Error displaying images: {str(e)}')
    #     return render_template('upload_image.html',token = session['token'])
    


@app.route("/admin_page",methods=['GET','POST'])
def admin_page():
    cur = conn.cursor()


    cur.execute("SELECT username FROM users")


    usernames = [row[0] for row in cur.fetchall()]

    cur.close()

    return render_template("admin_page.html",usernames = usernames)


@app.route("/remove_user", methods=['POST'])
def remove_user():
    try:
        data = request.json
        username = data.get('username')

        if not username:
            return jsonify({'success': False, 'message': 'Username not provided'})

        
        success = remove_user_from_database(username)

        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Failed to delete user'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


def remove_user_from_database(username):
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE username = %s", (username,))
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print("Error:", e)
        return False


# the code below stores in database as well as in directory

# @app.route('/changeprofile', methods=['POST'])
# def changeprofile():
#     if 'file' not in request.files:
#         return 'No file part', 400

#     file = request.files['file']

#     if file.filename == '':
#         return 'No selected file', 400

#     if file:
#         # Assuming you have a database connection named conn
#         cur = conn.cursor()
        
#         try:
#             # Ensure the folder for storing images exists
#             UPLOAD_FOLDER = 'static/images'
#             if not os.path.exists(UPLOAD_FOLDER):
#                 os.makedirs(UPLOAD_FOLDER)
            
#             # Save the file to the upload folder
#             file_path = os.path.join(UPLOAD_FOLDER, file.filename)
#             file.save(file_path)
            
#             # Open and read the image file in binary mode
#             with open(file_path, 'rb') as img_file:
#                 image_data = img_file.read()
#                 print("myname")
#                 cur.execute("""
#                     UPSERT INTO profile_pic (username, image_blob) 
#                     VALUES (%s, %s)
#                     """, (temp_user, image_data))
#                 conn.commit()
#                 print("aditya")
#                 return 'File uploaded successfully', 200
#         except Exception as e:
#             # Handle any errors that occur during file processing or database insertion
#             return f'Error: {str(e)}', 500
#         finally:
#             # Close the cursor
#             cur.close()

#     return 'Error uploading file', 500


@app.route('/changeprofile1', methods=['POST'])
def changeprofile1():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']

    if file.filename == '':
        return 'No selected file', 400

    if file:
        file_stream = BytesIO()
        file.save(file_stream)
        file_stream.seek(0)
        cur = conn.cursor()
           
        image_data = file_stream.read()
        print("myname")
        cur.execute("""
            UPSERT INTO profile_pic (username, image_blob) 
            VALUES (%s, %s)
            """, (temp_user, image_data))
        conn.commit()
        print("aditya")
        cur.close()
        return 'File uploaded successfully', 200

        
        

    return 'Error uploading file', 500


@app.route('/get_image', methods=['GET'])
def get_image():
    filename = request.args.get('filename')
    cursor = conn.cursor()
    print("hi")
    cursor.execute("SELECT image_blob FROM image_data WHERE filename = %s", (filename,))
    image_blob = cursor.fetchone()
    cursor.close()
    print("bye")
    
    if image_blob:
        image_bytes = image_blob[0]
        image_data = base64.b64encode(image_bytes).decode('utf-8')
        return jsonify({'imageData': image_data})
    else:
        return 'Image not found', 404



if __name__ == "__main__":
    app.run(debug="true")
