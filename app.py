from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import json
from urllib.parse import parse_qs

app = Flask(__name__)

# --------------------------------------
# Load the trained model
# --------------------------------------
try:
    model = joblib.load("model/text_emotion.pkl")
except Exception as e:
    print("Error loading model:", e)
    model = None

# --------------------------------------
# REQUIRED FOR TESTS: load_model()
# --------------------------------------
def load_model():
    """Returns the currently loaded ML model."""
    return model

# --------------------------------------
# REQUIRED FOR TESTS: preprocess_text()
# Very simple safe fallback for tests
# --------------------------------------
def preprocess_text(text: str) -> str:
    if text is None:
        return ""
    return str(text).strip()

# --------------------------------------
# Emotion emojis dictionary
# --------------------------------------
emotions_emoji_dict = {
    "anger": "😠",
    "fear": "😨😱",
    "happy/joy": "😂🤗",
    "love": "🥰",
    "neutral": "😐",
    "sadness": "😔",
    "surprise": "😮",
    "worry": "😔"
}

# --------------------------------------
# Predict emotion label
# --------------------------------------
def predict_emotions(docx):
    preprocessed = preprocess_text(docx)
    results = model.predict([preprocessed])
    return results[0]

# --------------------------------------
# Predict probabilities
# --------------------------------------
def get_prediction_proba(docx):
    preprocessed = preprocess_text(docx)
    results = model.predict_proba([preprocessed])
    return results

# --------------------------------------
# REQUIRED FOR CI + Kubernetes Probes
# /health endpoint
# --------------------------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

# --------------------------------------
# Home Page
# --------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

# --------------------------------------
# Helper: Parse raw body for text
# --------------------------------------
def extract_text(raw_data):
    try:
        data_str = raw_data.decode('utf-8')
        parsed_data = json.loads(data_str)
        text = parsed_data.get('text', '')
        return text
    except Exception as e:
        print("Error parsing raw data:", e)
        return ''

# --------------------------------------
# /predict API Endpoint
# --------------------------------------
@app.route('/predict', methods=['POST'])
def predict():
    try:
        raw_data = request.get_data()
        print("Raw Data:", raw_data)

        text = extract_text(raw_data)
        print("Input Text:", text)

        prediction = predict_emotions(text)
        probability = get_prediction_proba(text)

        max_index = np.argmax(probability)
        max_probability = probability[0][max_index]

        return jsonify({
            'text': text,
            'prediction': prediction,
            'probability': probability.tolist(),
            'max_probability': max_probability
        })

    except Exception as e:
        print("Error processing prediction:", e)
        return jsonify({'error': 'An error occurred while processing the prediction'}), 500


# --------------------------------------
# Start App
# --------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
