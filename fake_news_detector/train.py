import pandas as pd
import numpy as np
import nltk
import re
import joblib
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.utils import resample

# Download stopwords
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

# Load Dataset
df_fake = pd.read_csv(r"D:\fake_news_detector\datasets\fake_news.csv")
df_real = pd.read_csv(r"D:\fake_news_detector\datasets\real_news.csv")

# Rename columns if needed
df_fake.rename(columns={"statement": "text"}, inplace=True)
df_real.rename(columns={"statement": "text"}, inplace=True)

# Fill missing values
df_fake["text"] = df_fake["text"].fillna("")
df_real["text"] = df_real["text"].fillna("")

# Add labels (0 = Fake, 1 = Real)
df_fake["label"] = 0
df_real["label"] = 1

# Balance Dataset using Oversampling
if len(df_fake) < len(df_real):
    df_fake = resample(df_fake, replace=True, n_samples=len(df_real), random_state=42)
else:
    df_real = resample(df_real, replace=True, n_samples=len(df_fake), random_state=42)

# Merge datasets
df = pd.concat([df_fake, df_real]).sample(frac=1, random_state=42).reset_index(drop=True)

# Preprocessing function
def preprocess(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)  # Keep punctuation
    words = text.split()
    words = [word for word in words if word not in stop_words]
    return ' '.join(words)

df["processed_text"] = df["text"].astype(str).apply(preprocess)

# Remove empty rows
df = df[df["processed_text"].str.strip() != ""]

# Convert text into numerical features
vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1,2))
X = vectorizer.fit_transform(df["processed_text"])
y = df["label"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest Model
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# Evaluate Model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.4f}")
print(classification_report(y_test, y_pred))

# Save Model & Vectorizer
joblib.dump(model, r"D:\fake_news_detector\model\fake_news_model.pkl")
joblib.dump(vectorizer, r"D:\fake_news_detector\model\vectorizer.pkl")

print("Training Complete! Model saved.")
