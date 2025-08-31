from flask import Flask, render_template, request, redirect, url_for
import os
import joblib
import tensorflow as tf
import numpy as np
from werkzeug.utils import secure_filename
from PIL import Image
import cv2

app = Flask(__name__)

# Configure Upload Folder
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load Text and Image/Video Models
model = joblib.load("model/fake_news_model.pkl")
vectorizer = joblib.load("model/vectorizer.pkl")
image_video_model = tf.keras.models.load_model("model/deepfake_model.h5")

# Store news posts
news_posts = []

def preprocess_image(image_path):
    img = Image.open(image_path).resize((224, 224))
    img = np.array(img) / 255.0
    return np.expand_dims(img, axis=0)

def extract_video_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None
    frame = cv2.resize(frame, (224, 224))
    frame = frame / 255.0
    return np.expand_dims(frame, axis=0)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        news_text = request.form.get("news_text", "").strip()
        news_image = request.files.get("news_image")
        news_video = request.files.get("news_video")

        image_path = None
        video_path = None
        image_result = None
        video_result = None

        if news_image and news_image.filename:
            filename = secure_filename(news_image.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            news_image.save(save_path)
            image_path = f"uploads/{filename}"

            processed_img = preprocess_image(save_path)
            prediction = image_video_model.predict(processed_img)[0][0]
            image_result = "Real Image ✅" if prediction > 0.5 else "Fake Image ❌"

        if news_video and news_video.filename:
            filename = secure_filename(news_video.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            news_video.save(save_path)
            video_path = f"uploads/{filename}"

            frame = extract_video_frame(save_path)
            if frame is not None:
                prediction = image_video_model.predict(frame)[0][0]
                video_result = "Real Video ✅" if prediction > 0.5 else "Fake Video ❌"
            else:
                video_result = "Invalid Video ❌"

        text_result = None
        if news_text:
            transformed_text = vectorizer.transform([news_text])
            prediction = model.predict(transformed_text)[0]
            text_result = "Real News ✅" if prediction == 1 else "Fake News ❌"

        post_id = len(news_posts)
        news_posts.append({
            "id": post_id,
            "text": news_text,
            "image": image_path,
            "video": video_path,
            "text_result": text_result,
            "image_result": image_result,
            "video_result": video_result
        })

        return redirect(url_for("home"))

    return render_template("news.html", news_posts=news_posts)

@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    global news_posts
    if 0 <= post_id < len(news_posts):
        post = news_posts.pop(post_id)
        if post["image"]:
            image_file_path = os.path.join("static", post["image"])
            if os.path.exists(image_file_path):
                os.remove(image_file_path)
        if post["video"]:
            video_file_path = os.path.join("static", post["video"])
            if os.path.exists(video_file_path):
                os.remove(video_file_path)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
