from argparse import ArgumentParser
from tensorflow import keras
import numpy as np
import cv2
import os


def srgan(image_path):
    current_dir = os.getcwd()
    model_path=os.path.join(current_dir,'generator.h5')
    # Change model input shape to accept all size inputs
    model = keras.models.load_model(model_path.encode('utf-8'))
    inputs = keras.Input((None, None, 3))
    output = model(inputs)
    model = keras.models.Model(inputs, output)

        
    # Read image
    low_res = cv2.imread(image_path, 1)

    # Convert to RGB (opencv uses BGR as default)
    low_res = cv2.cvtColor(low_res, cv2.COLOR_BGR2RGB)

    # Rescale to 0-1.
    low_res = low_res / 255.0

    # Get super resolution image
    sr = model.predict(np.expand_dims(low_res, axis=0))[0]

    # Rescale values in range 0-255
    sr = (((sr + 1) / 2.) * 255).astype(np.uint8)

    # Convert back to BGR for opencv
    sr = cv2.cvtColor(sr, cv2.COLOR_RGB2BGR)

    # Save the results:
    current_dir = os.getcwd()
    submit_dir = os.path.join(current_dir, "submit")
    if not os.path.exists(submit_dir):
        os.makedirs(submit_dir)
        
    output_path = os.path.join(submit_dir, "test.jpg")
    cv2.imwrite(output_path, sr)
    
