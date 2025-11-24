from flask import Flask, render_template, request
import joblib
from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

# Load the trained model
model = joblib.load("model/text_emotion.pkl")

# Define a dictionary mapping emotions to emojis
emotions_emoji_dict = {
    "anger": "😠",  "fear": "😨😱", "happy/joy": "😂🤗",  
    "love": "🥰",  "neutral": "😐", "sadness": "😔", "surprise": "😮" , "worry": "😔"
}

# Function to predict emotions from text
def predict_emotions(docx):
    results = model.predict([docx])
    return results[0]

# Function to get prediction probabilities
def get_prediction_proba(docx):
    results = model.predict_proba([docx])
    return results

@app.route('/')
def index():
    return render_template('index.html')

from urllib.parse import parse_qs
import json

def parse_raw_data(raw_data):
    # Decode the raw data (bytes) to string
    data_str = raw_data.decode('utf-8')
    # Parse the string data into a dictionary
    parsed_data = parse_qs(data_str)
    return parsed_data

def extract_text(raw_data):
    try:
        data_str = raw_data.decode('utf-8')  # Decode raw data bytes to string
        parsed_data = json.loads(data_str)   # Parse string as JSON
        text = parsed_data.get('text', '')   # Extract 'text' field
        return text
    except Exception as e:
        print("Error parsing raw data:", e)
        return ''
    


@app.route('/predict', methods=['POST'])
def predict():
    try:
        raw_data = request.get_data()  # Get the raw request data
        print("Raw Data:", raw_data)

        text = extract_text(raw_data)  # Extract text from raw data
        print("Input Text:", text)

        # Perform prediction based on the extracted text
        prediction = predict_emotions(text)
        probability = get_prediction_proba(text)


        print("Probability:", probability) 
        
        
        max_index = np.argmax(probability)
        max_probability = probability[0][max_index]
        
        
        # Return prediction results as JSON
        return jsonify({
            'text': text,
            'prediction': prediction,
            'probability': probability.tolist(),
            'max_probability': max_probability
        })
    except Exception as e:
        print("Error processing prediction:", e)
        return jsonify({'error': 'An error occurred while processing the prediction'})

if __name__ == '__main__':
    app.run(debug=True)
