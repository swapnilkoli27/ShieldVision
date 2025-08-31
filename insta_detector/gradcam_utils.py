import numpy as np
import tensorflow as tf
import cv2
import matplotlib.cm as cm

def get_last_conv_layer(model):
    for layer in reversed(model.layers):
        if isinstance(layer, tf.keras.layers.Conv2D):
            return layer.name
    raise ValueError("No Conv2D layer found in the model.")

def generate_gradcam_heatmap(img_array, model, last_conv_layer_name):
    grad_model = tf.keras.models.Model(
        [model.inputs], [model.get_layer(last_conv_layer_name).output, model.output]
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        pred_index = tf.argmax(predictions[0])
        class_channel = predictions[:, pred_index]

    grads = tape.gradient(class_channel, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
    return heatmap.numpy()

def overlay_gradcam_on_image(original_img_path, img_array, model):
    last_conv_layer = get_last_conv_layer(model)
    heatmap = generate_gradcam_heatmap(img_array, model, last_conv_layer)

    img = cv2.imread(original_img_path)
    img = cv2.resize(img, (224, 224))

    heatmap_resized = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
    heatmap_colored = cm.jet(heatmap_resized)[:, :, :3]
    heatmap_colored = (heatmap_colored * 255).astype(np.uint8)

    overlay = cv2.addWeighted(img, 0.6, heatmap_colored, 0.4, 0)

    gradcam_path = original_img_path.replace(".jpg", "_gradcam.jpg").replace(".png", "_gradcam.png")
    cv2.imwrite(gradcam_path, overlay)

    return gradcam_path.replace("\\", "/")  # ✅ Fix for HTML compatibility


    return gradcam_path.replace("\\", "/")

if __name__ == "__main__":
    model = tf.keras.models.load_model("model/deepfake_model.h5")
    print("Last conv layer:", get_last_conv_layer(model))
