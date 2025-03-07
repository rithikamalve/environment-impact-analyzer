# EcoQuant AI

This project offers a web-based application designed to assess the environmental impact of products using machine learning. By analyzing product attributes such as water usage, carbon footprint, and energy consumption, the system predicts their environmental impact.

## Features

- 🌿 **Product Name Extraction:** Scrapes product names from URLs provided by the user.
- 🔗 **Groq API Integration:** Retrieves environmental data for products using the Groq API.
- 🧠 **Impact Prediction:** Utilizes a pre-trained machine learning model to forecast environmental impact.
- 💻 **User-Friendly Interface:** Provides a simple and clean interface for user interaction.

## Folder Structure

```plaintext
.env                    # Environment configuration file
app.py                  # Flask application
requirements.txt        # Dependency list for Python packages
notebooks/              # Jupyter notebooks and models
  ├── dataset.ipynb     # Data exploration and model training notebook
  └── environmental_impact_model.pkl  # Pre-trained ML model
static/                 # Static assets (CSS, JavaScript)
  └── styles.css        # Custom stylesheet
templates/              # Frontend templates
  └── index.html        # Main user interface template
```

## Prerequisites

Before starting, ensure you have the following:

- 🐍 **Python 3.9 or higher**

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd env-impact-analyzer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file and add the following:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Run the Flask server:**
   ```bash
   python app.py
   ```

5. **Access the application:**
   Open your browser and navigate to `http://127.0.0.1:5000`.

## Usage Instructions

- 🌐 **Provide a Product URL:** Enter a product URL to fetch product information.
- 📊 **Analyze Impact:** Use the pre-trained model to predict the product's environmental impact.
- ✅ **View Results:** Display the environmental data and impact classification.

## API Endpoints

### `GET /`
Displays the homepage.

### `POST /get_product_name`
Extracts the product name and retrieves environmental data.

#### Example Curl Request
```bash
curl -X POST -F "url=https://example-product-url.com" http://127.0.0.1:5000/get_product_name
```

## Machine Learning Model Details

The pre-trained model (`environmental_impact_model.pkl`) predicts the environmental impact based on the following features:

- 💧 **Water Usage (Liters)**
- 🌍 **Carbon Footprint (kg)**
- ⚡ **Energy Consumption (kWh)**

### Impact Classifications

- ✅ **Safe to Use:** Score <= 2
- ⚠️ **Use in Moderation:** 2 < Score <= 5
- ❌ **Not Safe to Use:** Score > 5

## Workflow

Below is the high-level workflow of the application:

1. 🌐 **User Interaction:**
   - User enters a product URL in the web interface.

2. 📥 **Data Extraction:**
   - The backend scrapes the product name from the given URL using BeautifulSoup.

3. 🔗 **API Request:**
   - The Groq API is called with the product name to retrieve environmental attributes.

4. 🧠 **Model Prediction:**
   - The retrieved attributes are passed to the pre-trained machine learning model to predict the environmental impact.

5. 📊 **Result Presentation:**
   - The prediction results are displayed on the frontend, showing impact categories and recommendations.

## Troubleshooting

### 🛠️ Template Not Found
Ensure the `index.html` file is in the `templates/` directory.

### 🎨 CSS File Not Loading
Verify that the CSS file is located inside the `static/` directory.

### 🔑 API Key Errors
Ensure that the `GROQ_API_KEY` in the `.env` file is correct.

## Future Improvements

- 🚀 **Model Enhancement:** Improve prediction accuracy.
- 🌐 **API Expansion:** Integrate additional APIs.
- 🎨 **UI Improvement:** Create a more intuitive user interface.

## License

This project is licensed under the [MIT License](LICENSE).

