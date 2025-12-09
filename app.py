# imports
import google.generativeai as genai
import requests
import json
import streamlit as st

# --- EDITED SECTION ---
# Set API keys securely from Streamlit's secrets
try:
    rapidapi_key = st.secrets["RAPIDAPI_KEY"]
    google_api_key = st.secrets["GOOGLE_API_KEY"]
except KeyError as e:
    st.error(f"ERROR: API key '{e.args[0]}' not found. Please check your .streamlit/secrets.toml file.")
    st.stop()

# --- NEW SECTION ---
# Configure the Google AI client
try:
    genai.configure(api_key=google_api_key)
except Exception as e:
    st.error(f"Failed to configure Google AI: {e}")
    st.stop()
# ----------------------


# This function is unchanged
def GetBitCoinPrices():
    # Define the API endpoint and query parameters
    url = "https://coinranking1.p.rapidapi.com/coin/Qwsogvtv82FCd/history"
    querystring = {
        "referenceCurrencyUuid": "yhjMzLPhuIDl",
        "timePeriod": "7d"
    }
    
    headers = {
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": "coinranking1.p.rapidapi.com"
    }
    
    try:
        response = requests.request(
            "GET", url, headers=headers, params=querystring)
        response.raise_for_status() 
        
        JSONResult = json.loads(response.text)
        history = JSONResult["data"]["history"]
        prices = []
        for change in history:
            prices.append(change["price"])
        
        pricesList = ','.join(prices)
        return pricesList

    except requests.exceptions.HTTPError as errh:
        st.error(f"HTTP Error: {errh}")
        st.error(f"API Response: {response.text}")
        return None
    except Exception as e:
        st.error(f"An error occurred in GetBitCoinPrices: {e}")
        return None

# --- THIS FUNCTION IS UNCHANGED ---
def AnalyzeBitCoin(bitcoinPrices):
    # The prompt is the same
    chatGPTPrompt = f"""You are an expert crypto trader with more than 10 years of experience, 
    I will provide you with a list of bitcoin prices for the last 7 days
    can you provide me with a technical analysis
    of Bitcoin based on these prices. here is what I want: 
    Price Overview, 
    Moving Averages, 
    Relative Strength Index (RSI),
    Moving Average Convergence Divergence (MACD),
    Advice and Suggestion,
    Do I buy or sell?
    Please be as detailed as you can, and explain in a way any beginner can understand. and make sure to use headings
    Here is the price list: {bitcoinPrices}"""

    try:
        # Using the best stable "pro" model from your list
        model = genai.GenerativeModel('models/gemini-pro-latest') 
        
        completion = model.generate_content(chatGPTPrompt)
        
        # Check if the response was blocked
        if not completion.parts:
            try:
                block_reason = completion.prompt_feedback.block_reason
            except Exception:
                block_reason = "Unknown (response was empty)"
            message = f"Sorry, your request was blocked by the safety filter. Reason: {block_reason}"
            st.error(message)
        else:
            message = completion.text.strip()
            
    except Exception as e:
        message = f"Sorry, I was not able to process your request with Gemini. Error: {e}"
        st.error(message)
    return message


st.title('Advanced Prompting With Python')
st.subheader(
    'Example: Analyzing Live Crypto Prices')

if st.button('Analyze'):
    bitcoinPrices = None 
    with st.spinner('Getting Bitcoin Prices...'):
        bitcoinPrices = GetBitCoinPrices()
    
    if bitcoinPrices:
        st.success('Bitcoin prices retrieved!')
        
        # --- THIS IS THE NEW DEBUG LINE ---
        #st.write(f"DEBUG: Price list is: [{bitcoinPrices}]")
        # ------------------------------------

        with st.spinner('Analyzing Bitcoin Prices (with Gemini Pro)...'):
            analysis = AnalyzeBitCoin(bitcoinPrices)
            st.text_area("Analysis", analysis,
                         height=500, max_chars=None, key=None,)
            st.success('Analysis complete!')
    else:
        st.error("Could not retrieve Bitcoin prices. Analysis cancelled.")