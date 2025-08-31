import os
import numpy as np
import librosa
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping

DATA_PATH = 'data'
LABELS = {'real': 0, 'fake': 1}
SAMPLE_RATE = 22050
DURATION = 3  # seconds
MFCC_FEATURES = 40

def extract_features(file_path):
    try:
        audio, sr = librosa.load(file_path, sr=SAMPLE_RATE, duration=DURATION)
        if len(audio) < DURATION * SAMPLE_RATE:
            padding = DURATION * SAMPLE_RATE - len(audio)
            audio = np.pad(audio, (0, padding))
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=MFCC_FEATURES)
        return mfcc
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def load_data():
    X = []
    y = []

    for label_str, label_int in LABELS.items():
        folder_path = os.path.join(DATA_PATH, label_str)
        for file in os.listdir(folder_path):
            if file.endswith(".wav") or file.endswith(".mp3"):
                path = os.path.join(folder_path, file)
                features = extract_features(path)
                if features is not None:
                    X.append(features)
                    y.append(label_int)

    X = np.array(X)
    y = np.array(y)
    return X, y

def build_model(input_shape):
    model = Sequential()
    model.add(Conv2D(32, (3, 3), activation='relu', input_shape=input_shape))
    model.add(MaxPooling2D((2, 2)))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2)))
    model.add(Flatten())
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(2, activation='softmax'))
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def main():
    print("Loading data...")
    X, y = load_data()

    X = X[..., np.newaxis]  # (samples, 40, ~130, 1)
    y = to_categorical(y, num_classes=2)

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    model = build_model(input_shape=X.shape[1:])
    print("Training model...")

    model.fit(
        X_train, y_train,
        epochs=20,
        batch_size=16,
        validation_data=(X_val, y_val),
        callbacks=[EarlyStopping(patience=3, restore_best_weights=True)]
    )

    model.save("deepfake_model.h5")
    print("Model saved as deepfake_model.h5")

if __name__ == "__main__":
    main()
