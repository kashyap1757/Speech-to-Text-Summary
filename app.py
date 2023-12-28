import os
import tensorflow as tf
import keras
import time
import wave
import pyaudio
import threading
import speech_recognition as sr
from keras.models import load_model
from flask import Flask, render_template, request, redirect, url_for, session,jsonify
#from flask_login import LoginManager,login_user,login_required,logout_user,current_user
from flask_sqlalchemy import SQLAlchemy
from text_summ import abs_summ
app = Flask(__name__)




#input_length_value = tf.shape(y_pred)[1]
#input_length_value = tf.cast(input_length_value, dtype=tf.int64)


# Some tensor you want to cast
tensor_to_cast = tf.constant([1, 2, 3])

# Cast the tensor to a different data type, for example, int64
casted_tensor = tf.cast(tensor_to_cast, dtype=tf.int64)

#import tensorflow.keras.backend as K
#from tensorflow.keras.utils import CustomObjectScope

# Custom CTC loss function
def CTCLoss_with_args(input_length, label_length, y_true=None, y_pred=None):
    def CTCLoss(y_true, y_pred):
    # Compute the training-time loss value
        batch_len = tf.cast(tf.shape(y_true)[0], dtype="int64")
        input_length = tf.cast(tf.shape(y_pred)[1], dtype="int64")
        label_length = tf.cast(tf.shape(y_true)[1], dtype="int64")

        input_length_value = tf.shape(y_pred)[1]
        input_length_value = tf.cast(input_length_value, dtype=tf.int64)
        input_length = input_length * tf.ones(shape=(batch_len, 1), dtype="int64")
        label_length = label_length * tf.ones(shape=(batch_len, 1), dtype="int64")

    loss = keras.backend.ctc_batch_cost(y_true, y_pred, input_length, label_length)
    pass
    return loss
    # Your CTC loss implementation

#input_length_value = tf.cast(tf.shape(y_pred)[1], dtype="int64")
#label_length_value = tf.cast(tf.shape(y_true)[1], dtype="int64")

#custom_loss =CTCLoss_with_args(input_length_value,label_length_value)
# Register the custom loss function with Keras
#with CustomObjectScope({'ctc_loss': custom_loss()}):
 #   model = load_model('model/SpeechToText.keras')


# Loading a Keras model
#model = load_model('model/SpeechToText.keras')





app.secret_key = '@890kkkd45?!890'  # Replace with a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database

db = SQLAlchemy(app)
@app.route('/index')
def index():
    return render_template('index.html')

# Define a User model for the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
class Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    text_to_summarize = db.Column(db.Text, nullable=False)
    generated_summary = db.Column(db.Text, nullable=False)
def create_tables():
    with app.app_context():
        db.create_all()
# Call the create_tables() function to create the tables within the Flask context
create_tables()
@app.route('/save_summary', methods=['POST','GET'])
def save_summary():
    user_id = session['user_id']  # Assuming you're using Flask-Login for authentication
    text_to_summarize = request.form.get('rawtext')
    abs_result=abs_summ(text_to_summarize)
    generated_summary = abs_result[1]  # Replace with your logic

    summary = Summary(user_id=user_id, text_to_summarize=text_to_summarize, generated_summary=generated_summary)
    db.session.add(summary)
    db.session.commit()
    return 'Summary saved successfully'

@app.route('/index1')
def index1():
    return render_template('index1.html')

@app.route('/a', methods=['GET', 'POST'])
def a():
    if request.method == 'POST':
        rawtext = request.form['rawtext']
        generated_summary, text_to_summarize, len_of_txt, len_of_smry = abs_summ(rawtext)

    user_id = session['user_id']  # Assuming you're using Flask-Login for authentication
    #text_to_summarize = request.form.get('rawtext')
    #abs_result = abs_summ(text_to_summarize)
    #generated_summary = abs_result[1]  # Replace with your logic

    summary = Summary(user_id=user_id, text_to_summarize=text_to_summarize, generated_summary=generated_summary)
    db.session.add(summary)
    db.session.commit()
    #return 'Summary saved successfully'
    return render_template('a.html', summary=generated_summary, original_text=text_to_summarize, len_of_txt=len_of_txt, len_of_smry=len_of_smry)

@app.route('/users')
def list_users():
    user_id = session['user_id']
    user = User.query.filter_by(id=user_id)
    summary = Summary.query.filter_by(user_id=user_id)
    return render_template('users.html', users=user,summary=summary)

output_folder = "recorded audio"
os.makedirs(output_folder,exist_ok=True)

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

audio=pyaudio.PyAudio()
frames=[]
recording=False
recording_thread=None

def record():
    global frames
    global recording
    recording=True
    stream=audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=0
    )
    frames=[]
    while recording:
        data=stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()

@app.route('/')
def page1():
    return render_template('page1.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username already exists in the database
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error_message="Username already exists. Please choose a different username.")

        # Create a new user and add it to the database
        new_user = User(username=username, password=password)
        with app.app_context():
            db.session.add(new_user)
            db.session.commit()
        return redirect(url_for('loginK'))

    return render_template('register.html')

# Route for login
@app.route('/loginK', methods=['GET', 'POST'])
def loginK():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists in the database
        user = User.query.filter_by(username=username).first()
        if not user:
            return render_template('loginK.html',error_message="Username invalid. Please register.")

        if user and user.password == password:
            session['username'] = user.username  # Store the username in the session
            session['user_id'] = user.id
            return render_template('index.html')
        else:
            #return render_template('register.html')
            return "please register first"

    return render_template('loginK.html')

# ... (other routes and code)
@app.route('/start_recording',methods=['POST'])
def start_recording():
    global recording
    global recording_thread
    recording=True
    recording_thread=threading.Thread(target=record)
    recording_thread.start()
    return redirect(url_for('index'))

@app.route('/stop_recording',methods=['POST'])
def stop_recording():
    global recording
    global recording_thread
    recording=False
    recording_thread.join()

    timestamp=int(time.time())
    output_filename=os.path.join(output_folder,f"audio_{timestamp}.wav")

    with wave.open(output_filename,"wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))

        recognizer = sr.Recognizer()
        with sr.AudioFile(output_filename) as source:
            audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio_data)
            return jsonify({'text_result': text})
        except sr.UnknownValueError:
            return jsonify({'text_result': "Could not understand the audio"})
    """ except sr.RequestError as e:
            return jsonify({'text_result': f"Could not request results; {e}"})
    """
    #return render_template('index.html',audio_saved=output_filename)

if __name__=="__main__":
    app.run(debug=True)
