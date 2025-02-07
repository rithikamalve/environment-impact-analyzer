import json
import pickle
import os
import re
import requests
from flask import Flask, request, render_template
from bs4 import BeautifulSoup
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from preprocess import get_preprocessor,preprocess_data
import pandas as pd

# Load the trained model at the start of the app
with open('environmental_impact_model.pkl', 'rb') as f:
    model = pickle.load(f)

app = Flask(__name__)

# Route to render the homepage
@app.route('/')
def home():
    return render_template('index.html')

# Function to extract product name from a URL using BeautifulSoup
def get_product_name(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")  # Debugging statement
        return f"Error fetching page: {e}"

    soup = BeautifulSoup(response.text, "html.parser")

    # Try extracting from common tags and attributes directly
    attribute_selectors = [
        "data-tag-product-name", "data-product-title", "data-name", "itemprop", 
        "data-product-name", "product-name", "title", "og:title", "twitter:title",
        "h1.product-title", "h1.title", "h1.product-name", "span.product-title", 
        "meta[name='title']", "meta[property='og:title']"
    ]
    
    product_names = []
    for attr in attribute_selectors:
        product_tag = soup.find(attrs={attr: True})
        if product_tag and attr in product_tag.attrs:
            product_names.append(product_tag.attrs.get(attr).strip())

    # If no product names are found in attributes, check common HTML tags for title-like content
    tag_selectors = [
        "h1.product-title", "h1.title", "h1.product-name",
        "span[itemprop='name']", "span.product-title", "meta[property='og:title']",
        "meta[name='title']", "meta[property='twitter:title']", "div.product-name",
        "div.product-title", "span.product-name", "span.product-title",
        "meta[name='product-name']"
    ]
    
    for selector in tag_selectors:
        if "meta" in selector:
            meta_tag = soup.select_one(selector)
            if meta_tag and meta_tag.get("content"):
                product_names.append(meta_tag["content"])
        else:
            product_element = soup.select_one(selector)
            if product_element:
                product_names.append(product_element.get_text(strip=True))

    if not product_names and soup.title:
        product_names.append(soup.title.get_text(strip=True))

    # Clean the extracted names and remove unwanted characters
    cleaned_names = [re.sub(r'\s+', ' ', name).strip() for name in product_names]

    if cleaned_names:
        longest_name = max(cleaned_names, key=len)
        print(f"Extracted Product Name: {longest_name}")  # Debugging statement
        return longest_name

    print("Product name not found")  # Debugging statement
    return "Product name not found"

# Fetch environmental data from Groq API
def fetch_groq_data(product_name):
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    if not GROQ_API_KEY:
        print("GROQ API Key not found.")  # Debugging statement
        return None

    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant that provides product environmental information in JSON format."},
        {"role": "user", "content": f"Please provide environmental information about {product_name} in JSON format with these fields: materials, category, brand, manufacturing_location, water_usage_liters, carbon_footprint_kg, energy_consumption_kwh"}
    ]
    
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(GROQ_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        groq_data = response.json()
        
        assistant_response = groq_data['choices'][0]['message']['content']
        
        json_match = re.search(r'(\{.*\})', assistant_response, re.DOTALL)
        if json_match:
            clean_response = json_match.group(1)
            print(f"Clean Response from Groq: {clean_response}")  # Debugging statement
        else:
            print("No valid JSON found in the response from Groq.")  # Debugging statement
            return None
        
        clean_response = clean_response.replace("\\_", "_")
        product_data = json.loads(clean_response)
        
        product_info = {
            "Materials": product_data.get("materials", "Not Available"),
            "Category": product_data.get("category", "Not Available"),
            "Brand": product_data.get("brand", "Not Available"),
            "Manufacturing Location": product_data.get("manufacturing_location", "Not Available"),
            "Water Usage (L)": float(product_data.get("water_usage_liters", 0)),
            "Carbon Footprint (kg)": float(product_data.get("carbon_footprint_kg", 0)),
            "Energy Consumption (kWh)": float(product_data.get("energy_consumption_kwh", 0))
        }
        print(f"Fetched Product Info: {product_info}")  # Debugging statement
        return product_info
        
    except Exception as e:
        print(f"Error fetching Groq data: {e}")  # Debugging statement
        return None

# Function to make predictions based on the environmental data
def predict_environmental_impact(product_info):
    try:
        # Extract the preprocessor pipeline
        preprocessor = get_preprocessor()

        # Create a DataFrame with default structure for fitting
        dummy_data = pd.DataFrame([{
            "Materials": "", "Category": "", "Brand": "", "Manufacturing Location": "",
            "Water Usage (L)": 0, "Carbon Footprint (kg)": 0, "Energy Consumption (kWh)": 0
        }])
        
        # Fit the preprocessor once with dummy data
        preprocessor.fit(dummy_data)

        # Preprocess the data
        preprocessed_data = preprocess_data(product_info, preprocessor)

        # Predict using the trained model
        output = model.predict(preprocessed_data)[0]
        print(f"Predicted Environmental Impact Score: {output}")  # Debugging statement

        return {
            'score': float(output),
            'classification': classify_environmental_impact(output)
        }

    except Exception as e:
        print(f"Error in prediction: {e}")  # Debugging statement
        return None


# Classify the environmental impact score
def classify_environmental_impact(score):
    if score <= 2:
        return "Safe to Use"
    elif 2 < score <= 5:
        return "Use in Moderation"
    else:
        return "Not Safe to Use"

# Flask route to handle product name extraction, API data fetching, and prediction
@app.route('/get_product_name', methods=['POST'])
def handle_product_name():
    product_url = request.form.get("url")
    if not product_url:
        print("Error: No URL provided.")  # Debugging statement
        return render_template("index.html", error="Please provide a product URL.")

    product_name = get_product_name(product_url)
    if product_name == "Product name not found" or product_name.startswith("Error"):
        print(f"Error: Could not extract product name from URL.")  # Debugging statement
        return render_template("index.html", error="Couldn't extract the product name from the provided URL.")

    print(f"Extracted Product Name: {product_name}")  # Debugging statement
    
    product_info = fetch_groq_data(product_name)
    if not product_info:
        print(f"Error: Failed to fetch environmental information for {product_name}.")  # Debugging statement
        return render_template("index.html", error="Failed to fetch environmental information from Groq API.")
    
    prediction_result = predict_environmental_impact(product_info)
    if not prediction_result:
        print("Error: Prediction failed.")  # Debugging statement
        return render_template("index.html", error="Prediction failed. Please try again later.")
    
    return render_template(
        "index.html",
        product_name=product_name,
        product_info=product_info,
        prediction_result=prediction_result
    )

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
