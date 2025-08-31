from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from tensorflow.keras.models import load_model
import librosa
import numpy as np
from pydub import AudioSegment

# Initialize Flask
app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load model
model_path = os.path.join(os.path.dirname(__file__), 'deepfake_model.h5')
if not os.path.exists(model_path):
    raise FileNotFoundError("Trained model not found! Place 'deepfake_model.h5' in 'backend/'.")

model = load_model(model_path)
print("Loaded model. Expected input shape:", model.input_shape)


def predict_audio(file_path):
    try:
        SAMPLE_RATE = 22050
        DURATION = 3
        MFCC_FEATURES = 40

        print("Original file:", file_path)

        # Convert to wav if it's not already
        if not file_path.endswith(".wav"):
            wav_path = file_path + ".wav"
            audio = AudioSegment.from_file(file_path)
            audio = audio.set_channels(1)  # mono
            audio = audio.set_frame_rate(SAMPLE_RATE)
            audio.export(wav_path, format="wav")
            file_path = wav_path
            print("Converted to WAV:", file_path)

        # Load and pad/truncate
        audio, sr = librosa.load(file_path, sr=SAMPLE_RATE, duration=DURATION)
        if len(audio) < DURATION * SAMPLE_RATE:
            padding = DURATION * SAMPLE_RATE - len(audio)
            audio = np.pad(audio, (0, padding))

        # Extract MFCC
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=MFCC_FEATURES)
        mfcc = np.expand_dims(mfcc, axis=-1)  # Add channel
        mfcc = np.expand_dims(mfcc, axis=0)   # Add batch

        print("Model input shape:", mfcc.shape)

        prediction = model.predict(mfcc)
        label = np.argmax(prediction)
        return "Real Audio" if label == 0 else "Deepfake Audio"

    except Exception as e:
        print("Error during prediction:", e)
        return "Error during prediction"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        result = predict_audio(file_path)
        return jsonify({"result": result})
    except Exception as e:
        print("Error during prediction:", e)  # This will show the real error in terminal
        return jsonify({"result": "Error during prediction"}), 500


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, port=5002)

