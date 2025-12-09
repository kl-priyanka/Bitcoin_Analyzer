import google.generativeai as genai
import toml
import os

# --- Configuration ---
# Path to your secrets file
SECRETS_FILE = os.path.join(".streamlit", "secrets.toml")
# ---------------------

print(f"Attempting to read secrets from: {SECRETS_FILE}")

try:
    # 1. Read the secrets.toml file
    secrets = toml.load(SECRETS_FILE)
    api_key = secrets.get("GOOGLE_API_KEY")

    if not api_key:
        print(f"Error: 'GOOGLE_API_KEY' not found in {SECRETS_FILE}")
        exit()
    
    print("API Key found. Configuring client...")

    # 2. Configure the genai client
    genai.configure(api_key=api_key)

    print("Successfully configured API key. Fetching available models...")
    print("==========================================================")
    print("MODELS YOUR KEY CAN USE:")

    # 3. List all models
    found_models = False
    for model in genai.list_models():
        # 4. Check which models support the 'generateContent' method
        if 'generateContent' in model.supported_generation_methods:
            print(f"  -> {model.name}")
            found_models = True

    if not found_models:
        print("No models supporting 'generateContent' were found for your API key.")
        
    print("==========================================================")
    print("\nPlease copy one of the 'models/...' names from the list above (e.g., 'models/gemini-1.5-flash-latest')")
    print("and paste it into the 'genai.GenerativeModel(...)' line in your app.py file.")

except FileNotFoundError:
    print(f"Error: The file {SECRETS_FILE} was not found.")
    print(f"Please make sure you are running this script from your main project directory ({os.getcwd()})")
except Exception as e:
    print(f"An error occurred: {e}")