from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import xgboost as xgb
import json
import numpy as np
from datetime import datetime
import requests
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# ---------------- Security Headers ----------------
@app.after_request
def apply_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Content-Security-Policy'] = "default-src 'self'; frame-ancestors 'none'"
    return response

# ---------------- Coordinates Database ----------------
coordinates = {
    "Laguna": {
        "City of Biñan": { "lat": 14.3388, "lon": 121.0842 }, 
        "City of Cabuyao": { "lat": 14.2796, "lon": 121.1236 }, 
        "City of Calamba": { "lat": 14.2060, "lon": 121.1556 }, 
        "City of San Pablo": { "lat": 14.0701, "lon": 121.3256 }, 
        "City of San Pedro": { "lat": 14.3639, "lon": 121.0568 }, 
        "City of Santa Rosa": { "lat": 14.3146, "lon": 121.1137 }, 
        "Alaminos": { "lat": 14.0631, "lon": 121.2481 }, 
        "Bay": { "lat": 14.1810, "lon": 121.2848 }, 
        "Calauan": { "lat": 14.1454, "lon": 121.3150 }, 
        "Cavinti": { "lat": 14.2647, "lon": 121.5455 }, 
        "Famy": { "lat": 14.4344, "lon": 121.4492 }, 
        "Kalayaan": { "lat": 14.3276, "lon": 121.4804 }, 
        "Liliw": { "lat": 14.1364, "lon": 121.4399 }, 
        "Los Baños": { "lat": 14.1788, "lon": 121.2408 }, 
        "Luisiana": { "lat": 14.1908, "lon": 121.5094 }, 
        "Lumban": { "lat": 14.2975, "lon": 121.4591 }, 
        "Mabitac": { "lat": 14.4338, "lon": 121.4263 }, 
        "Magdalena": { "lat": 14.1996, "lon": 121.4293 }, 
        "Majayjay": { "lat": 14.1447, "lon": 121.4723 }, 
        "Nagcarlan": { "lat": 14.1366, "lon": 121.4160 }, 
        "Paete": { "lat": 14.3644, "lon": 121.4814 }, 
        "Pagsanjan": { "lat": 14.2727, "lon": 121.4557 }, 
        "Pakil": { "lat": 14.3811, "lon": 121.4787 }, 
        "Pangil": { "lat": 14.4029, "lon": 121.4678 }, 
        "Pila": { "lat": 14.3000, "lon": 121.3500 }, 
        "Rizal": { "lat": 14.3667, "lon": 121.4333 }, 
        "Santa Cruz": { "lat": 14.3333, "lon": 121.4167 }, 
        "Santa Maria": { "lat": 14.3000, "lon": 121.4333 }, 
        "Siniloan": { "lat": 14.4681, "lon": 121.4852 }, 
        "Victoria": { "lat": 14.2316, "lon": 121.3278 }, 
    },
    "Cavite": {
        "City of Bacoor": { "lat": 14.4587, "lon": 120.9386 }, 
        "City of Carmona": { "lat": 14.309243, "lon": 121.031708 }, 
        "City of Dasmariñas": { "lat": 14.3268, "lon": 120.9411 }, 
        "City of General Trias": { "lat": 14.3861637, "lon": 120.8802798 }, 
        "City of Imus": { "lat": 14.4289, "lon": 120.9367 }, 
        "City of Tagaytay": { "lat": 14.115286, "lon": 120.962112 }, 
        "Trece Martires City": { "lat": 14.28, "lon": 120.87 }, 
        "Alfonso": { "lat": 14.1380464, "lon": 120.8554205 }, 
        "Amadeo": { "lat": 14.209, "lon": 120.905 }, 
        "General Emilio Aguinaldo": { "lat": 14.243, "lon": 120.842 }, 
        "Indang": { "lat": 14.227, "lon": 120.929 }, 
        "Kawit": { "lat": 14.427, "lon": 120.897 }, 
        "Magallanes": { "lat": 14.215, "lon": 120.727 }, 
        "Maragondon": { "lat": 14.234, "lon": 120.689 }, 
        "Mendez": { "lat": 14.133333, "lon": 120.9 }, 
        "Naic": { "lat": 14.201, "lon": 120.821 }, 
        "Noveleta": { "lat": 14.375, "lon": 120.908 }, 
        "Rosario": { "lat": 14.305, "lon": 120.907 }, 
        "Silang": { "lat": 14.215, "lon": 120.92 }, 
        "Tanza": { "lat": 14.305, "lon": 120.88 }, 
        "Ternate": { "lat": 14.350, "lon": 120.757 },
    },
    "Batangas": { 
        "City of Batangas": { "lat": 13.7567, "lon": 121.0584 }, 
        "City of Calaca": { "lat": 13.9354, "lon": 120.8137 }, 
        "City of Lipa": { "lat": 13.9419, "lon": 121.1644 }, 
        "City of Santo Tomas": { "lat": 14.1000, "lon": 121.1667 }, 
        "City of Tanauan": { "lat": 14.0836, "lon": 121.1497 }, 
        "Agoncillo": { "lat": 13.9183, "lon": 120.9186 }, 
        "Alitagtag": { "lat": 13.8778, "lon": 121.0025 }, 
        "Balayan": { "lat": 13.9373, "lon": 120.7322 }, 
        "Balete": { "lat": 14.0167, "lon": 121.1000 }, 
        "Bauan": { "lat": 13.7911, "lon": 121.0083 }, 
        "Calatagan": { "lat": 13.8322, "lon": 120.6339 }, 
        "Cuenca": { "lat": 13.9000, "lon": 121.0500 }, 
        "Ibaan": { "lat": 13.8167, "lon": 121.1333 }, 
        "Laurel": { "lat": 14.0500, "lon": 120.9167 }, 
        "Lemery": { "lat": 13.8833, "lon": 120.8667 }, 
        "Lian": { "lat": 14.0000, "lon": 120.6500 }, 
        "Lobo": { "lat": 13.6500, "lon": 121.2167 }, 
        "Mabini": { "lat": 13.7500, "lon": 120.9167 }, 
        "Malvar": { "lat": 14.0500, "lon": 121.1500 }, 
        "Mataasnakahoy": { "lat": 13.9500, "lon": 121.0833 }, 
        "Nasugbu": { "lat": 14.0667, "lon": 120.6333 }, 
        "Padre Garcia": { "lat": 13.8833, "lon": 121.2167 }, 
        "Rosario": { "lat": 13.8500, "lon": 121.2000 }, 
        "San Jose": { "lat": 13.8833, "lon": 121.1000 }, 
        "San Juan": { "lat": 13.8333, "lon": 121.4000 }, 
        "San Luis": { "lat": 13.8333, "lon": 120.9833 }, 
        "San Nicolas": { "lat": 13.9333, "lon": 120.9333 }, 
        "San Pascual": { "lat": 13.8000, "lon": 121.0333 }, 
        "Santa Teresita": { "lat": 13.8833, "lon": 121.0167 }, 
        "Taal": { "lat": 13.8833, "lon": 120.9333 }, 
        "Talisay": { "lat": 14.1000, "lon": 121.0167 }, 
        "Taysan": { "lat": 13.8167, "lon": 121.2000 }, 
        "Tingloy": { "lat": 13.6500, "lon": 120.8500 }, 
        "Tuy": { "lat": 14.0167, "lon": 120.7333 },
    },
    "Rizal": { 
        "City of Antipolo": { "lat": 14.5870, "lon": 121.1758 }, 
        "Angono": { "lat": 14.5333, "lon": 121.1500 }, 
        "Baras": { "lat": 14.5166, "lon": 121.2666 }, 
        "Binangonan": { "lat": 14.4667, "lon": 121.1921 }, 
        "Cainta": { "lat": 14.5780, "lon": 121.1163 }, 
        "Cardona": { "lat": 14.3819, "lon": 121.2068 }, 
        "Jalajala": { "lat": 14.3950, "lon": 121.4530 }, 
        "Morong": { "lat": 14.4485, "lon": 121.4398 }, 
        "Pililla": { "lat": 14.4461, "lon": 121.2869 }, 
        "Rodriguez": { "lat": 14.6780, "lon": 121.1278 }, 
        "San Mateo": { "lat": 14.6522, "lon": 121.0859 }, 
        "Tanay": { "lat": 14.5372, "lon": 121.2956 }, 
        "Taytay": { "lat": 14.5733, "lon": 121.1160 }, 
        "Teresa": { "lat": 14.5833, "lon": 121.2250 },
    },
    "Quezon": { 
        "City of Tayabas": { "lat": 14.0259, "lon": 121.5929 }, 
        "Agdangan": { "lat": 13.8758, "lon": 121.9122 }, 
        "Alabat": { "lat": 14.1138, "lon": 122.0497 }, 
        "Atimonan": { "lat": 13.9966, "lon": 121.9180 }, 
        "Buenavista": { "lat": 13.7225, "lon": 122.4241 }, 
        "Burdeos": { "lat": 14.8436, "lon": 121.9697 }, 
        "Calauag": { "lat": 13.9575, "lon": 122.2878 }, 
        "Candelaria": { "lat": 13.9289, "lon": 121.4247 }, 
        "Casiguran": { "lat": 16.2278, "lon": 122.0633 }, 
        "Claveria": { "lat": 13.9000, "lon": 122.1500 }, 
        "Dolores": { "lat": 14.0225, "lon": 121.4113 }, 
        "General Luna": { "lat": 13.6998, "lon": 122.2314 }, 
        "General Nakar": { "lat": 14.7570, "lon": 121.6209 }, 
        "Guinayangan": { "lat": 13.8460, "lon": 122.2260 }, 
        "Gumaca": { "lat": 13.9210, "lon": 122.1016 }, 
        "Infanta": { "lat": 14.6519, "lon": 121.6518 }, 
        "Jomalig": { "lat": 13.9833, "lon": 122.7833 }, 
        "Lopez": { "lat": 13.8001, "lon": 122.3108 }, 
        "Lucban": { "lat": 14.1143, "lon": 121.5548 }, 
        "Lucena": { "lat": 13.9314, "lon": 121.6172 }, 
        "Macalelon": { "lat": 13.8360, "lon": 122.2000 }, 
        "Mauban": { "lat": 14.1040, "lon": 121.6380 },
    }
}

# ---------------- Weather Fetcher ----------------
def get_weather_from_open_meteo(lat, lon):
    """Fetch temperature, humidity, and rainfall data from Open-Meteo API."""
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&hourly=temperature_2m,relative_humidity_2m,precipitation"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Take latest available values
        latest_index = len(data['hourly']['time']) - 1
        temp = data['hourly']['temperature_2m'][latest_index]
        humidity = data['hourly']['relative_humidity_2m'][latest_index]
        rainfall = data['hourly']['precipitation'][latest_index]

        return temp, humidity, rainfall
    except Exception as e:
        print(f"Weather fetch error: {e}")
        return None, None, None

# ---------------- Load Model ----------------
try:
    with open('xgboost_model_train_api.json', 'r') as f:
        model_data = json.load(f)
    model = xgb.Booster()
    model.load_model('xgboost_model_train_api.json')
    feature_names = model_data['learner']['feature_names']
except FileNotFoundError:
    print("Error: xgboost_model_train_api.json not found. Please ensure the file is in the backend directory.")
    exit(1)
except Exception as e:
    print(f"Error loading model: {str(e)}")
    exit(1)

# ---------------- Disease Map ----------------
disease_map = {
    0: "Rice Blast",
    1: "Brown Spot",
    2: "Sheath Blight",
    3: "Leaf Scald",
    4: "Stem Rot",
    5: "False Smut",
    6: "Bacterial Leaf Blight",
    7: "Rice Tungro",
    8: "Neck Blast",
    9: "Panicle Blight",
    10: "Grain Discoloration",
    11: "Sheath Rot",
    12: "Bakanae",
    13: "Udbatta",
    14: "Red Stripe",
    15: "Healthy"
}

# ---------------- Serve HTML Templates ----------------
@app.route('/', defaults={'path': 'home.html'})
@app.route('/<path:path>')
def serve_html(path):
    valid_paths = ['home.html', 'prediction.html', 'results.html', 'signin.html', 'climate.html', 'health.html', 'knowledge.html']
    if path in valid_paths:
        return render_template(path)
    return render_template('home.html')

@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/favicon.ico')
def no_favicon():
    return '', 204  # 204 No Content stops the request without error

# ---------------- Prediction Endpoint ----------------
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["province", "municipality", "barangay", "predictionRange"]
        if not data or not all(k in data for k in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        province = data['province']
        municipality = data['municipality']
        barangay = data.get('barangay', '')

        # Get coordinates
        if province not in coordinates or municipality not in coordinates[province]:
            return jsonify({"error": f"No coordinates found for {municipality}, {province}"}), 400

        lat = coordinates[province][municipality]["lat"]
        lon = coordinates[province][municipality]["lon"]

        # Fetch weather
        temp, humidity, rainfall = get_weather_from_open_meteo(lat, lon)

        if temp is None:
            return jsonify({"error": "Failed to fetch weather data"}), 500

        # Current date
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month

        # Build feature vector
        feature_vector = [
            year, month, 0, 0, 0,            
            rainfall, temp, temp, temp, humidity, 0,  
            temp, temp, temp,                
            temp, temp, temp,                
            temp, temp, temp,                
            humidity, humidity,              
            rainfall, rainfall, rainfall,    
            0, 0                             
        ]

        # Validate feature length
        if len(feature_vector) != len(feature_names):
            return jsonify({
                "error": f"Feature vector length mismatch. Expected {len(feature_names)}, got {len(feature_vector)}"
            }), 400

        # Predict
        dmatrix = xgb.DMatrix([feature_vector], feature_names=feature_names)
        prediction = model.predict(dmatrix)[0]

        predicted_class = int(round(prediction))
        predicted_disease = disease_map.get(predicted_class, "Unknown Disease")

        return jsonify({
            "predictedDisease": predicted_disease,
            "temperature": temp,
            "humidity": humidity,
            "rainfall": rainfall
        })

    except Exception as e:
        print(f"Prediction error: {str(e)}")
        print(f"Predicting for {municipality}, {province}: Temp={temp}, Hum={humidity}, Rain={rainfall}")
        return jsonify({"error": f"Prediction error: {str(e)}"}), 500

# ---------------- Run Server ----------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
else:
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)