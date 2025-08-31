from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import joblib
import tensorflow as tf
import numpy as np
from werkzeug.utils import secure_filename
from PIL import Image
import cv2
from get_prediction_reason import get_prediction_reason
from gradcam_utils import overlay_gradcam_on_image

app = Flask(__name__)

# Upload Folder
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load Models
model = joblib.load("model/fake_news_model.pkl")
vectorizer = joblib.load("model/vectorizer.pkl")
image_video_model = tf.keras.models.load_model("model/deepfake_model.h5")

# Store posts
news_posts = []

# Prediction Threshold
THRESHOLD = 0.5

# Preprocess image
def preprocess_image(image_path):
    img = Image.open(image_path).resize((224, 224)).convert('RGB')
    img = np.array(img) / 255.0
    img = np.expand_dims(img, axis=0)
    return img

# Extract frame from video
def extract_video_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return None
    frame = cv2.resize(frame, (224, 224))
    frame = frame / 255.0
    frame = np.expand_dims(frame, axis=0)
    return frame

@app.route("/", methods=["GET", "POST"])
def home():
    image_result = None
    video_result = None
    image_path = None
    video_path = None
    text_result = None
    news_text = None

    if request.method == "POST":
        news_image = request.files.get("news_image")
        news_video = request.files.get("news_video")
        news_text = request.form.get("news_text")

        # Image handling
        if news_image and news_image.filename:
            filename = secure_filename(news_image.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            news_image.save(save_path)
            image_path = f"static/uploads/{filename}"

            processed_img = preprocess_image(save_path)
            prediction = image_video_model.predict(processed_img)[0][0]
            print(f"🔥 Image Prediction Score: {prediction}")

            is_real = prediction > THRESHOLD
            is_fake = not is_real
            reason = get_prediction_reason(media_type="image", is_fake=is_fake)
            result_text = "Real Image ✅" if is_real else "Fake Image ❌"
            image_result = f"{result_text} - {reason}"

        # Video handling
        if news_video and news_video.filename:
            filename = secure_filename(news_video.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            news_video.save(save_path)
            video_path = f"static/uploads/{filename}"

            frame = extract_video_frame(save_path)
            if frame is not None:
                prediction = image_video_model.predict(frame)[0][0]
                print(f"🔥 Video Prediction Score: {prediction}")

                is_real = prediction > THRESHOLD
                is_fake = not is_real
                reason = get_prediction_reason(media_type="video", is_fake=is_fake)
                result_text = "Real Video ✅" if is_real else "Fake Video ❌"
                video_result = f"{result_text} - {reason}"
            else:
                video_result = "Could not process video frame."

        # Text handling
        if news_text:
            transformed_text = vectorizer.transform([news_text])
            prediction = model.predict(transformed_text)[0]
            text_result = "Real News ✅" if prediction == 1 else "Fake News ❌"

        news_posts.append({
            "text": news_text,
            "image": image_path,
            "video": video_path,
            "text_result": text_result,
            "image_result": image_result,
            "video_result": video_result
        })

        return redirect(url_for("home"))

    return render_template("insta.html", news_posts=news_posts)

@app.route("/analyze_post", methods=["POST"])
def analyze_post():
    try:
        news_text = request.form.get("text")
        image_file = request.files.get("image")
        video_file = request.files.get("video")

        image_result = None
        video_result = None
        text_result = None

        # Analyze text
        if news_text:
            transformed = vectorizer.transform([news_text])
            prediction = model.predict(transformed)[0]
            text_result = "Real News ✅" if prediction == 1 else "Fake News ❌"

        # Analyze image
        if image_file:
            filename = secure_filename(image_file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image_file.save(path)
            processed = preprocess_image(path)
            prediction = image_video_model.predict(processed)[0][0]
            print(f"🔥 Image Prediction Score (Analyze API): {prediction}")

            is_real = prediction > THRESHOLD
            is_fake = not is_real
            reason = get_prediction_reason(media_type="image", is_fake=is_fake)
            result_text = "Real Image ✅" if is_real else "Fake Image ❌"
            image_result = f"{result_text} - {reason}"

            try:
                gradcam_path = overlay_gradcam_on_image(path, processed, image_video_model)
                image_result += f"<br><img src='/{gradcam_path}' width='224' height='224'>"
            except Exception as e:
                print("🔥 Grad-CAM Error (Image):", e)
                image_result = image_result or ""
                image_result += "<br>⚠️ Explanation generation failed."

        # Analyze video
        if video_file:
            filename = secure_filename(video_file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            video_file.save(path)
            frame = extract_video_frame(path)
            if frame is not None:
                prediction = image_video_model.predict(frame)[0][0]
                print(f"🔥 Video Prediction Score (Analyze API): {prediction}")

                is_real = prediction > THRESHOLD
                is_fake = not is_real
                reason = get_prediction_reason(media_type="video", is_fake=is_fake)
                result_text = "Real Video ✅" if is_real else "Fake Video ❌"
                video_result = f"{result_text} - {reason}"

                frame_img_path = path.replace(".mp4", "_frame.jpg")
                cv2.imwrite(frame_img_path, (frame[0] * 255).astype(np.uint8))
                try:
                    gradcam_path = overlay_gradcam_on_image(frame_img_path, frame, image_video_model)
                    video_result += f"<br><img src='/{gradcam_path}' width='224' height='224'>"
                except Exception as e:
                    print("🔥 Grad-CAM Error (Video):", e)
                    video_result = video_result or ""
                    video_result += "<br>⚠️ Explanation generation failed."
            else:
                video_result = "Invalid Video ❌"

        return jsonify({
            "text_result": text_result,
            "image_result": image_result,
            "video_result": video_result
        })

    except Exception as e:
        print("🔥 SERVER ERROR:", e)
        return jsonify({
            "error": "Internal Server Error. Please check backend logs."
        }), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
