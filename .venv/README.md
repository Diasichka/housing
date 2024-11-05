
---

# House Price Prediction Pipeline

This project implements a data processing and prediction pipeline for house prices using a pre-trained model (`model.joblib`). The pipeline loads, processes, and predicts house prices based on input data in `housing.csv`, saves the results in a SQLite database (`housing_data.db`), and exposes the functionality via a REST API built with Flask.

## Project Structure

- **`api.py`**: Flask application that exposes API endpoints for data preprocessing, prediction, and retrieving predictions.
- **`main.py`**: Core pipeline code that loads data, preprocesses it, generates predictions, and handles database storage.
- **`housing.csv`**: Sample dataset used to test and demonstrate the pipeline.
- **`housing_data.db`**: SQLite database to store preprocessed data and predictions.
- **`model.joblib`**: Pre-trained machine learning model used for house price predictions.
- **`requirements.txt`**: List of required Python packages for the project.

## Setup and Installation

1. **Clone the repository**: 
   ```bash
   git clone <repository-url>
   ```

2. **Navigate to the project directory**:
   ```bash
   cd py_RDD
   ```

3. **Create a virtual environment and activate it**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   source .venv/bin/activate  # On macOS/Linux
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Pipeline

Run `main.py` to execute the full pipeline: load data, preprocess it, generate predictions, and save everything in the database.
   ```bash
   python main.py 
   ```

## REST API Endpoints

1. **Start the Flask API**:
   ```bash
   python api.py
   ```

2. **Available Endpoints**:

   - **`POST /preprocess`**: Preprocesses the data and saves it to the database.
   - **`POST /predict`**: Generates predictions using the pre-trained model and saves them to the database.
   - **`GET /predictions`**: Retrieves all saved predictions from the database.

   Example of calling the **`/predict`** endpoint:
   ```bash
   Invoke-RestMethod -Uri http://127.0.0.1:5000/predict -Method Post
   ```

## Testing

The project includes unit tests to verify the functionality of each part of the pipeline.

1. **Run tests**:
   ```bash
   python -m unittest discover tests
   ```

## Sample Inputs and Expected Outputs

You can validate predictions based on sample data inputs and outputs provided below:

- **Input 1**:
   ```yaml
   longitude: -122.64
   latitude: 38.01
   housing_median_age: 36.0
   total_rooms: 1336.0
   total_bedrooms: 258.0
   population: 678.0
   households: 249.0
   median_income: 5.5789
   ocean_proximity: 'NEAR OCEAN'
   ```
   **Output**: `320201.58554044`

- **Input 2**:
   ```yaml
   longitude: -115.73
   latitude: 33.35
   housing_median_age: 23.0
   total_rooms: 1586.0
   total_bedrooms: 448.0
   population: 338.0
   households: 182.0
   median_income: 1.2132
   ocean_proximity: 'INLAND'
   ```
   **Output**: `58815.45033765`

- **Input 3**:
   ```yaml
   longitude: -117.96
   latitude: 33.89
   housing_median_age: 24.0
   total_rooms: 1332.0
   total_bedrooms: 252.0
   population: 625.0
   households: 230.0
   median_income: 4.4375
   ocean_proximity: '<1H OCEAN'
   ```
   **Output**: `192575.77355635`

## Notes

- **Python Version**: This project is tested with Python 3.9.13.
- **Database File**: `housing_data.db` is generated and updated as the pipeline runs.
- **License**: Data and model are distributed under a public license.

---

## Optional Tasks and Topics for Discussion

### 1. Logging - How and Why to Implement It?

**Why Logging?**  
Logging is essential for tracking the flow of a program, understanding where errors occur, and monitoring operations in real time. In a data pipeline, `logging` helps capture the stages of data loading, preprocessing, and prediction, making it easier to debug and ensure data flows correctly through each stage.

**How Logging is Implemented**  
In this project, logging is implemented using Python's `logging` module:

- Each step in the `HousingPipeline` class logs important actions, such as when data is loaded, processed, or when predictions are generated.
- Logging levels (`INFO`, `ERROR`) help distinguish between normal operations and errors.

**Additional Logging Recommendations**

For a production system, consider:

- Configuring different logging levels for development (`DEBUG`) and production (`ERROR`).
- Writing logs to a file for historical tracking.
- Adding more detailed logs at every stage, especially for data validation and model prediction steps.

### 2. Tests - How and Why to Implement Them?

**Why Testing?**  
Tests ensure that the pipeline behaves as expected. They help validate data loading, preprocessing transformations, and predictions, giving confidence that each part of the pipeline is functioning correctly.

**How Testing is Implemented**  
In this project, the `unittest` framework is used to create test cases:

- **Data Loading Test**: Verifies that data is loaded into the database correctly.
- **Preprocessing Test**: Checks if data transformations, especially one-hot encoding, were successful.
- **Prediction Test**: Uses a mock model to test if predictions are generated and saved correctly.

**Further Testing Suggestions**

- **Edge Case Tests**: Test for cases with missing data or unexpected data types.
- **Integration Tests**: Ensure all pipeline stages work together seamlessly.

### 3. Exception Handling - How and Why to Implement It?

**Why Exception Handling?**  
Exception handling ensures the pipeline can handle unexpected issues gracefully, logging errors instead of crashing the program.

**How Exception Handling is Implemented**  
The project uses `try-except` blocks to manage errors:

- Database connections are wrapped in `try-except-finally` blocks to ensure they close even if an error occurs.
- Exceptions are logged with descriptive messages to help diagnose issues.

**Further Recommendations**

- Use specific exception types (e.g., `FileNotFoundError`, `ValueError`) for targeted handling.
- Implement fallback mechanisms for critical steps to ensure the pipeline continues running even if minor parts fail.

### 4. API - How and Why to Implement It?

**Why an API?**  
An API allows external applications or users to interact with the pipeline easily. This enables them to preprocess data, generate predictions, and retrieve results without directly accessing the code.

**How the API is Implemented**  
In this project, Flask provides endpoints to interact with the pipeline:

- **`/preprocess`** (POST): Triggers the data preprocessing step.
- **`/predict`** (POST): Runs the model to generate predictions.
- **`/get_predictions`** (GET): Returns the generated predictions from the database.

**Future API Enhancements**

- **Authentication**: Use token-based authentication to secure the API.
- **Error Handling**: Return HTTP error codes (e.g., 400 for bad requests).
- **Pagination**: Add pagination to `get_predictions` for efficient data retrieval.

---

 