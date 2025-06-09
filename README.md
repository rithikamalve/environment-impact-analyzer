# Environmental Impact Analyzer for Cosmetic Products (a.k.a EcoQuant AI)

Welcome to the **Environmental Impact Analyzer**, a machine learning-powered web application designed to evaluate the sustainability of cosmetic and personal care products. By leveraging a synthetic dataset and a stacking ensemble model, this tool calculates an **Environmental Impact Score (EIS)** for products based on their ecological footprint, empowering users to make eco-conscious choices.

**[Live Demo](#)** | **[GitHub Repository](#)**

## Table of Contents
- [Project Overview](#project-overview)
- [Dataset Description](#dataset-description)
- [Stacking Ensemble Model](#stacking-ensemble-model)
- [Workflow and Module Connectivity](#workflow-and-module-connectivity)
- [Installation and Setup](#installation-and-setup)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The Environmental Impact Analyzer enables users to assess the environmental footprint of cosmetic products by inputting a product URL. The system retrieves relevant environmental attributes, processes them through a stacking ensemble machine learning model, and outputs an EIS along with a classification (Safe, Moderate, or Unsafe). Built with a Flask backend, a frontend interface, and the Grok API for data retrieval, this project combines data science and user-friendly design to promote sustainability in the cosmetic industry.

## Dataset Description

The dataset is a synthetic collection generated using a Large Language Model (LLM) to simulate real-world data for cosmetic and personal care products. It includes the following attributes:

- **product_name (string)**: Name of the product.
- **brand (string)**: Manufacturing company or brand.
- **water_usage_liters (float)**: Water consumed (in liters) during the product’s lifecycle.
- **carbon_footprint_kg (float)**: Carbon dioxide emissions (in kilograms).
- **energy_consumption_kwh (float)**: Energy used (in kilowatt-hours) during production and distribution.
- **packaging_waste_g (float)**: Packaging waste (in grams) per product.
- **biodegradability (float: 0–100)**: Percentage of the product that decomposes naturally.
- **hazardous_chemicals (integer or binary)**: Number of toxic chemicals.
- **recyclability_score (float: 0–10)**: Recyclability of packaging and materials.
- **environmental_impact_score (float: 0–100)**: Composite score of the product’s environmental impact (target variable).

This dataset forms the foundation for training and evaluating the stacking ensemble model.

## Stacking Ensemble Model

The core of the analyzer is a **stacking ensemble model** for regression, which predicts the `environmental_impact_score`. The model combines multiple base learners using a meta-learner to improve predictive accuracy.

### Base Models
The following base regression models are used:
- Random Forest Regressor
- XGBoost Regressor
- LightGBM Regressor
- Support Vector Regressor (SVR)
- K-Nearest Neighbors Regressor
- Ridge Regression
- ElasticNet Regression

### Methodology
1. **Out-of-Fold (OOF) Predictions**:
   - A `get_oof_predictions()` function uses K-Fold cross-validation (typically 5 folds) to generate:
     - `train_stack`: OOF predictions for the training set.
     - `test_stack`: Averaged predictions for the test set.
   - This prevents data leakage and ensures robust predictions.

2. **Base Model Training**:
   - Each base model is retrained on the full training dataset for final predictions.

3. **Meta-Learner**:
   - An XGBoost Regressor serves as the meta-learner.
   - Hyperparameters are tuned over a grid (`n_estimators`: [50, 100, 200], `learning_rate`: [0.01, 0.05, 0.1], `max_depth`: [3, 4, 5]) using 5-fold cross-validation and negative mean squared error.
   - The meta-learner is trained on `train_stack` and predicts on `test_stack`.

4. **Evaluation**:
   - Metrics: Root Mean Squared Error (RMSE) and Coefficient of Determination (R²).
   - Feature importances from the meta-learner indicate which base models contribute most to predictions.

## Workflow and Module Connectivity

The project follows a seamless workflow to process user inputs and deliver sustainability insights. The module connectivity diagram illustrates the data flow:

![Module Connectivity Diagram](.png)

### Workflow Steps
1. **User Input**:
   - Users submit a product URL via the web application’s frontend interface.

2. **Backend Processing**:
   - The Flask backend receives the URL and invokes the **Grok API** (provided by xAI) to retrieve environmental attributes (e.g., water usage, carbon footprint).

3. **Data Preprocessing**:
   - Attributes are standardized, cleaned, and validated to ensure consistency.

4. **Model Prediction**:
   - Validated data is fed into the pre-trained stacking ensemble model.
   - The model calculates the **Environmental Impact Score (EIS)** and classifies it as:
     - **Safe**: Low environmental impact.
     - **Moderate**: Medium impact.
     - **Unsafe**: High impact.

5. **Result Delivery**:
   - The Flask backend sends the EIS, classification, and environmental assessment to the frontend.
   - The frontend displays results with visualizations (e.g., charts or gauges) for user-friendly interpretation.

This workflow ensures a smooth and intuitive experience for evaluating cosmetic product sustainability.

## Installation and Setup

To run the Environmental Impact Analyzer locally, follow these steps:

### Prerequisites
- Python 3.8+
- Flask
- scikit-learn, xgboost, lightgbm, pandas, numpy
- Grok API key (obtain from [xAI API](https://console.groq.com/keys))
- Git

### Installation
1. Clone the repository:
   ```bash
   git clone <your-github-repo-link>
   cd <repository-name>
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the root directory.
   - Add your Groq API key:
     ```plaintext
     GROQ_API_KEY=<your-api-key>
     ```

5. Run the Flask application:
   ```bash
   python app.py
   ```

6. Access the web application at `http://localhost:5000`.

## Usage

1. Open the web application in your browser.
2. Enter a product URL (e.g., from an e-commerce site) in the input field.
3. Submit the URL to receive the EIS, classification (Safe/Moderate/Unsafe), and detailed environmental assessment.
4. Explore visualizations to understand the product’s sustainability metrics.

For a live demo, visit [[Live Demo](#)](https://ecoquant-ai.onrender.com/).


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
