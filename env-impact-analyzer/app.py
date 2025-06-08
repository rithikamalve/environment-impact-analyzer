import json
import pickle
import os
import re
import requests
from flask import Flask, request, render_template,jsonify
from bs4 import BeautifulSoup
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pandas as pd
from dotenv import load_dotenv
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import joblib
from groq import Groq
import traceback
import requests
import os

def download_file_from_google_drive(file_id, destination):
    """
    Downloads a file from Google Drive given its file ID and saves it to the destination path.
    """
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()

    response = session.get(URL, params={'id': file_id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)

def get_confirm_token(response):
    """
    Extracts a download confirmation token from the response cookies (if present).
    """
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def save_response_content(response, destination):
    """
    Writes the downloaded file content in chunks to avoid memory overload.
    """
    CHUNK_SIZE = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)

load_dotenv()

import cloudpickle  # add this import at the top

file_id = "13309QGIMz7tf0e7vUGvl8pDfY1rgkDgw"
destination = "environmental_pipeline_v2.pkl"

model = None

if not os.path.exists(destination):
    print("[INFO] Model not found. Downloading from Google Drive...")
    download_file_from_google_drive(file_id, destination)
    print("[INFO] Download complete.")

# Load the model only once
try:
    with open(destination, "rb") as f:
        model = cloudpickle.load(f)  # change here from pickle.load to cloudpickle.load
    print("[INFO] Model loaded successfully.")
except Exception as e:
    print("[ERROR] Failed to load model:", e)





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
    print(f"[INFO] Starting Groq data fetch for product: {product_name}")
    print("API_KEY from .env:", os.getenv("GROQ_API_KEY"))

    API_KEY=os.getenv("GROQ_API_KEY")
    client = Groq(api_key=API_KEY)  
    try:
        if not product_name:
            print("[ERROR] Missing 'product_name'")
            return jsonify({"error": "Missing 'product_name'"}), 400

        # Prepare dynamic prompt
        system_prompt = f"""
            Generate environmental impact data for this cosmetic product: {product_name}

            Return ONLY valid JSON with these fields:
            - materials: common ingredients
            - category: product category
            - brand: brand name
            - manufacturing_location: location of production
            - water_usage_liters: water used (float)
            - carbon_footprint_kg: carbon emissions (float)
            - energy_consumption_kwh: energy used (float)
            - packaging_waste_g: packaging waste (float)
            - biodegradability: score from 0-1 (float)
            - hazardous_chemicals: number of chemicals (int)
            - recyclability_score: score from 1-10 (int)
            """

        print("[INFO] Sending request to Groq model...")
        response = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": product_name}
            ],
            temperature=0.3,
            max_tokens=1024,
            top_p=1,
            stream=False
        )

        raw_output = response.choices[0].message.content
        print("[DEBUG] Raw model output:\n", raw_output)

        # Try to extract JSON
        match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', raw_output) or re.search(r'(\{[\s\S]*?\})', raw_output)
        if match:
            json_str = match.group(1)
            print("[INFO] JSON detected. Attempting to parse...")
            product_data = json.loads(json_str)
            print("[SUCCESS] Parsed JSON:", product_data)
            return product_data
        else:
            print("[ERROR] No valid JSON structure found in response.")
            return jsonify({"error": "No valid JSON found in model response."}), 500

    except Exception as e:
        print("[EXCEPTION] Something went wrong during model interaction:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    

def generate_synthetic_data(product_name):
    # Extract brand from product name
    brand = product_name.split('-')[-1].strip() if '-' in product_name else "Unknown"
    
    # Make educated guesses about the product category
    if any(term in product_name.lower() for term in ["lip", "tint", "matte"]):
        category = "Cosmetics - Lip Products"
    elif any(term in product_name.lower() for term in ["foundation", "concealer"]):
        category = "Cosmetics - Face Products" 
    elif any(term in product_name.lower() for term in ["mascara", "eyeshadow", "eyeliner"]):
        category = "Cosmetics - Eye Products"
    else:
        category = "Cosmetics"
        
    # Generate realistic but synthetic data
    import random
    
    # Seed with product name for consistency
    random.seed(hash(product_name) % 10000)
    
    # Dictionary of manufacturing locations by common cosmetic brands
    brand_locations = {
        "Maybelline": "United States",
        "L'Oreal": "France",
        "Revlon": "United States",
        "NYX": "South Korea",
        "MAC": "Canada",
        "Fenty": "Italy",
        "Clinique": "United States",
        "Estee Lauder": "United Kingdom"
    }
    
    # Common cosmetic materials
    materials_options = [
        "Glycerin, Isododecane, Dimethicone, Synthetic Wax",
        "Petrolatum, Paraffin, Ozokerite, Mineral Oil",
        "Polybutene, Isopropyl Myristate, Silica, Beeswax",
        "Cyclopentasiloxane, Octyldodecanol, Microcrystalline Wax"
    ]
    
    product_data = {
        "materials": random.choice(materials_options),
        "category": category,
        "brand": brand,
        "manufacturing_location": brand_locations.get(brand, "China"),
        "water_usage_liters": round(random.uniform(0.5, 4.0), 1),
        "carbon_footprint_kg": round(random.uniform(0.2, 1.5), 2),
        "energy_consumption_kwh": round(random.uniform(0.1, 2.0), 2),
        "packaging_waste_g": round(random.uniform(5, 30), 1),
        "biodegradability": round(random.uniform(0.1, 0.7), 2),
        "hazardous_chemicals": random.randint(0, 5),
        "recyclability_score": random.randint(2, 8)
    }
    print(product_data)
    return product_data


# Function to make predictions based on the environmental data
def predict_environmental_impact(product_data):
    try:
        # Handle the case where product_data is a Response object
        if hasattr(product_data, 'get_json'):
            product_data = product_data.get_json()
            
        # Now product_data should be a dictionary
        input_df = pd.DataFrame([product_data])
        
        # Only calculate features that don't depend on the target variable
        input_df['sustainability_ratio'] = (input_df['recyclability_score'] + 3) / (input_df['packaging_waste_g'] + 3)
        input_df['toxicity_index'] = input_df['hazardous_chemicals'] - input_df['biodegradability']
        input_df['resource_efficiency'] = (input_df['water_usage_liters'] + input_df['energy_consumption_kwh']) / 2
        
        # Load the saved pipeline
        model = joblib.load("environmental_pipeline.pkl")
        
        # Predict using the loaded pipeline
        output = model.predict(input_df)[0]
        print(f"Predicted Environmental Impact Score: {output}")  # Debug
        
        return {
            'score': round(float(output),2),
            'classification': classify_environmental_impact(output)
        }
    
    except Exception as e:
        print(f"Error in prediction: {e}")
        traceback.print_exc()  # Print the full stack trace
        return None

# Classify the environmental impact score
def classify_environmental_impact(score):
    if score <= 0.3:
        return "Safe to Use"
    elif 0.3 < score <= 0.7:
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
    
    # Convert keys to match HTML expectations
    product_info = {
        "Water Usage (L)": product_info["water_usage_liters"],
        "Carbon Footprint (kg)": product_info["carbon_footprint_kg"],
        "Energy Consumption (kWh)": product_info["energy_consumption_kwh"]
    }

    return render_template(
        "index.html",
        product_name=product_name,
        product_info=product_info,
        prediction_result=prediction_result
    )


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
