import os
import unittest
import pandas as pd
import sqlite3
from unittest.mock import patch, MagicMock
from main import HousingPipeline

class TestHousingPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Obtain the absolute path to the housing.csv file
        cls.csv_path = os.path.join(os.path.dirname(__file__), '..', 'housing.csv')
        cls.model_path = os.path.join(os.path.dirname(__file__), '..', 'model.joblib')
        cls.db_path = 'test_housing_data.db'

        # Check for housing.csv file
        if not os.path.exists(cls.csv_path):
            raise FileNotFoundError(f"CSV file not found: {cls.csv_path}")

        # Initializing the pipeline with an absolute path
        cls.pipeline = HousingPipeline(cls.csv_path, cls.model_path, cls.db_path)

        # Loading data into the database
        cls.pipeline.load_data_to_db()

    def test_load_data(self):
        conn = sqlite3.connect(self.pipeline.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM housing_data")
        count = cursor.fetchone()[0]
        conn.close()
        self.assertGreater(count, 0, "Data loading failed - table is empty")

    def test_preprocess_data(self):
        # Perform data preprocessing after the data has been downloaded
        self.pipeline.preprocess_data()
        conn = sqlite3.connect(self.pipeline.db_path)
        data = pd.read_sql_query("SELECT * FROM housing_data_transformed LIMIT 1", conn)
        conn.close()
        self.assertIn('ocean_proximity_NEAR BAY', data.columns, "Preprocessing failed - encoded column missing")

    @patch("main.load", return_value=MagicMock())
    def test_generate_predictions(self, mock_model):
        mock_model.return_value.feature_names_in_ = [
            'longitude', 'latitude', 'housing_median_age', 'total_rooms', 'total_bedrooms',
            'population', 'households', 'median_income', 'ocean_proximity_<1H OCEAN',
            'ocean_proximity_INLAND', 'ocean_proximity_ISLAND', 'ocean_proximity_NEAR BAY',
            'ocean_proximity_NEAR OCEAN'
        ]
        mock_model.return_value.predict.return_value = [100000.0] * 20639

        self.pipeline.preprocess_data()
        self.pipeline.generate_predictions()

        conn = sqlite3.connect(self.pipeline.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM housing_predictions")
        count = cursor.fetchone()[0]
        conn.close()
        self.assertGreater(count, 0, "Prediction generation failed - no predictions saved")

    @classmethod
    def tearDownClass(cls):
        # Deleting the database after all tests have been completed
        try:
            os.remove(cls.pipeline.db_path)
        except PermissionError:
            print(f"Error: The file {cls.pipeline.db_path} is still open.")

if __name__ == '__main__':
    unittest.main()
