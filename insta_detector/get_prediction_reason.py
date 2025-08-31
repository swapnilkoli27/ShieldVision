import random

def get_prediction_reason(media_type="image", is_fake=True):
    fake_reasons = {
        "image": [
            "Face blending artifacts detected.",
            "Unusual skin texture found.",
            "Eye alignment looks unnatural.",
            "Pixel noise suggests manipulation.",
            "Facial features seem off."
        ],
        "video": [
            "Lip sync mismatch detected.",
            "Eye movement seems robotic.",
            "Frame flickering indicates deepfake.",
            "Unnatural head motion found.",
            "Inconsistent facial expressions over time."
        ]
    }

    real_reasons = {
        "image": [
            "Natural facial structure and lighting.",
            "No signs of image tampering.",
            "Consistent skin tone and texture.",
            "Normal eye and mouth alignment.",
            "No manipulation artifacts found."
        ],
        "video": [
            "Smooth and consistent motion.",
            "Natural lip and eye movement.",
            "No frame-level irregularities.",
            "Stable facial expressions throughout.",
            "No visual distortions or glitches."
        ]
    }

    if is_fake:
        return random.choice(fake_reasons[media_type])
    else:
        return random.choice(real_reasons[media_type])
