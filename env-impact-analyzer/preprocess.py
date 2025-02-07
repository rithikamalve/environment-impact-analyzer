import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

# Define feature categories
categorical_features = ['Materials', 'Category', 'Brand', 'Manufacturing Location']
numeric_features = ['Water Usage (L)', 'Carbon Footprint (kg)', 'Energy Consumption (kWh)']

def get_preprocessor():
    """
    Returns the preprocessor pipeline for data transformations.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ]
    )
    return preprocessor

def preprocess_data(product_info, preprocessor):
    """
    Prepares and transforms the input data for prediction.
    """
    # Convert dictionary to a DataFrame
    data = pd.DataFrame([product_info])
    
    # Ensure all required columns exist, fill missing if necessary
    for col in categorical_features + numeric_features:
        if col not in data:
            data[col] = 0 if col in numeric_features else ''
    
    # Transform the data
    preprocessed_data = preprocessor.transform(data)
    return preprocessed_data
