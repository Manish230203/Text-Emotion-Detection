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
    if model is None:
        raise RuntimeError("Model not loaded")
    results = model.predict([preprocessed])
    # convert numpy types to Python native
    if isinstance(results, np.ndarray):
        val = results[0]
        return val.item() if hasattr(val, "item") else val
    # if list-like
    return results[0]

# --------------------------------------
# Predict probabilities (return numpy array)
# --------------------------------------
def get_prediction_proba(docx):
    preprocessed = preprocess_text(docx)
    if model is None:
        raise RuntimeError("Model not loaded")
    results = model.predict_proba([preprocessed])
    # normalize to numpy array for consistent handling
    return np.asarray(results)

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
        # not JSON — try form-style parsing
        try:
            s = raw_data.decode('utf-8')
            parsed = parse_qs(s)
            # parse_qs returns lists for values
            if 'text' in parsed and parsed['text']:
                return parsed['text'][0]
        except Exception:
            pass
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
        probability_arr = get_prediction_proba(text)  # numpy array

        # Ensure probability_arr is 2D and has first-row probabilities
        probability_arr = np.atleast_2d(np.asarray(probability_arr))
        probability_list = probability_arr.tolist()  # safe Python-native list

        # compute max probability safely
        try:
            max_index = int(np.argmax(probability_arr[0]))
            max_probability = float(probability_arr[0][max_index])
        except Exception:
            # fallbacks
            max_index = 0
            max_probability = float(probability_list[0][0]) if probability_list and probability_list[0] else 0.0

        # Ensure prediction is native Python type
        if isinstance(prediction, np.generic):
            prediction = prediction.item()

        return jsonify({
            'text': text,
            'prediction': prediction,
            'probability': probability_list,
            'max_probability': max_probability
        }), 200

    except Exception as e:
        print("Error processing prediction:", e)
        return jsonify({'error': 'An error occurred while processing the prediction', 'detail': str(e)}), 500


# --------------------------------------
# Start App
# --------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
