from flask import Flask, jsonify, request
from main import HousingPipeline
import sqlite3
import pandas as pd

app = Flask(__name__)
pipeline = HousingPipeline(data_path='housing.csv', model_path='model.joblib', db_path='housing_data.db')

@app.route('/preprocess', methods=['POST'])
def preprocess_data():
    pipeline.preprocess_data()
    return jsonify({"status": "Data preprocessed successfully"}), 200

@app.route('/predict', methods=['POST'])
def predict():
    pipeline.generate_predictions()
    return jsonify({"status": "Predictions generated successfully"}), 200

@app.route('/get_predictions', methods=['GET'])
def get_predictions():
    conn = sqlite3.connect(pipeline.db_path)
    data = pd.read_sql("SELECT * FROM housing_predictions", conn)
    conn.close()
    return jsonify(data.to_dict(orient="records")), 200

if __name__ == '__main__':
    app.run(debug=True)

