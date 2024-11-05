import pandas as pd
import numpy as np
import sqlite3
from joblib import load
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
import logging
import sys
from colorama import init, Fore
import os

init(autoreset=True)

logging.basicConfig(level=logging.INFO, format=f"{Fore.CYAN}%(asctime)s - %(levelname)s - %(message)s",
                    stream=sys.stdout)


class HousingPipeline:
    def __init__(self, data_path, model_path, db_path):
        self.data_path = data_path
        self.model_path = model_path
        self.db_path = db_path

    def load_data_to_db(self, table_name='housing_data'):
        conn = None
        try:
            if not os.path.exists(self.data_path):
                raise FileNotFoundError(f"File not found: {self.data_path}")

            logging.info("Loading data from CSV into the database...")
            data = pd.read_csv(self.data_path)

            data.columns = [
                "longitude", "latitude", "housing_median_age", "total_rooms",
                "total_bedrooms", "population", "households", "median_income",
                "median_house_value", "ocean_proximity", "agency"
            ]

            conn = sqlite3.connect(self.db_path)
            data.to_sql(table_name, conn, if_exists='replace', index=False)
            logging.info(f"Data successfully loaded into '{table_name}' table in the database.")
        except Exception as e:
            logging.error(f"Error loading data into the database: {e}")
        finally:
            if conn:
                conn.close()

    def preprocess_data(self, table_name='housing_data', output_table='housing_data_transformed'):
        conn = None
        try:
            logging.info("Starting data preprocessing...")
            conn = sqlite3.connect(self.db_path)
            data = pd.read_sql(f"SELECT * FROM {table_name}", conn)

            # Replace invalid values with NaN
            data.replace("Null", np.nan, inplace=True)

            # Code the categorical column 'ocean_proximity'
            encoder = OneHotEncoder(sparse=False)
            ocean_encoded = encoder.fit_transform(data[['ocean_proximity']])
            encoded_columns = encoder.get_feature_names_out(['ocean_proximity'])
            ocean_encoded_df = pd.DataFrame(ocean_encoded, columns=encoded_columns)

            # Link the coded data to the main table
            data = pd.concat([data.drop(columns=['ocean_proximity', 'agency']), ocean_encoded_df], axis=1)

            # Add missing categories if necessary
            all_possible_categories = [
                'ocean_proximity_<1H OCEAN', 'ocean_proximity_INLAND',
                'ocean_proximity_ISLAND', 'ocean_proximity_NEAR BAY',
                'ocean_proximity_NEAR OCEAN'
            ]
            for category in all_possible_categories:
                if category not in data.columns:
                    data[category] = 0

            # Handling missing values using the median
            imputer = SimpleImputer(strategy='median')
            data_imputed = pd.DataFrame(imputer.fit_transform(data), columns=data.columns)

            # Saving preprocessed data
            data_imputed.to_sql(output_table, conn, if_exists='replace', index=False)
            logging.info("Preprocessed data saved to the database.")
        except Exception as e:
            logging.error(f"Error during data preprocessing: {e}")
        finally:
            if conn:
                conn.close()

    def generate_predictions(self, input_table='housing_data_transformed', output_table='housing_predictions'):
        conn = None
        try:
            logging.info("Loading model for predictions...")
            model = load(self.model_path)

            conn = sqlite3.connect(self.db_path)
            data = pd.read_sql(f"SELECT * FROM {input_table}", conn)

            # Check for feature_names_in_ and select features
            if hasattr(model, 'feature_names_in_'):
                expected_features = model.feature_names_in_
                features = data.reindex(columns=expected_features, fill_value=0)
            else:
                logging.warning("Model does not have 'feature_names_in_' attribute. Using data columns directly.")
                features = data.drop(columns=['median_house_value'], errors='ignore')

            if features.empty:
                raise ValueError("No features matched between input data and model expectations.")

            # Generating predictions and saving the results
            predictions = model.predict(features)

            if len(predictions) != len(data):
                raise ValueError("Mismatch between number of predictions and input data rows")

            data['predicted_price'] = predictions
            data.to_sql(output_table, conn, if_exists='replace', index=False)
            logging.info("Predictions successfully saved to the database.")
        except Exception as e:
            logging.error(f"Error generating predictions: {e}")
        finally:
            if conn:
                conn.close()

    def test_sample_predictions(self):
        logging.info("Running test predictions for sample data...")

        sample_data = pd.DataFrame([
            {"longitude": -122.64, "latitude": 38.01, "housing_median_age": 36.0, "total_rooms": 1336.0,
             "total_bedrooms": 258.0, "population": 678.0, "households": 249.0, "median_income": 5.5789,
             "ocean_proximity": "NEAR OCEAN"},
            {"longitude": -115.73, "latitude": 33.35, "housing_median_age": 23.0, "total_rooms": 1586.0,
             "total_bedrooms": 448.0, "population": 338.0, "households": 182.0, "median_income": 1.2132,
             "ocean_proximity": "INLAND"},
            {"longitude": -117.96, "latitude": 33.89, "housing_median_age": 24.0, "total_rooms": 1332.0,
             "total_bedrooms": 252.0, "population": 625.0, "households": 230.0, "median_income": 4.4375,
             "ocean_proximity": "<1H OCEAN"}
        ])

        encoder = OneHotEncoder(sparse=False)
        ocean_encoded = encoder.fit_transform(sample_data[['ocean_proximity']])
        encoded_columns = encoder.get_feature_names_out(['ocean_proximity'])
        ocean_encoded_df = pd.DataFrame(ocean_encoded, columns=encoded_columns)

        sample_data = pd.concat([sample_data.drop(columns=['ocean_proximity']), ocean_encoded_df], axis=1)

        all_possible_categories = [
            'ocean_proximity_<1H OCEAN', 'ocean_proximity_INLAND',
            'ocean_proximity_ISLAND', 'ocean_proximity_NEAR BAY',
            'ocean_proximity_NEAR OCEAN'
        ]
        for category in all_possible_categories:
            if category not in sample_data.columns:
                sample_data[category] = 0

        model = load(self.model_path)
        sample_data = sample_data.reindex(columns=model.feature_names_in_)
        predictions = model.predict(sample_data)

        for i, pred in enumerate(predictions, start=1):
            logging.info(f"Prediction for sample {i}: {pred}")


if __name__ == "__main__":
    pipeline = HousingPipeline(data_path='housing.csv', model_path='model.joblib', db_path='housing_data.db')
    pipeline.load_data_to_db()
    pipeline.preprocess_data()
    pipeline.generate_predictions()
    pipeline.test_sample_predictions()
