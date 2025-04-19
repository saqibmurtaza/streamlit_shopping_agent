from google.generativeai import configure
from agents import Agent, Runner, OpenAIChatCompletionsModel, function_tool, set_tracing_disabled
from agents.run import RunConfig
import google.generativeai as genai
import streamlit as st
import sys

try:
    # Get configuration from Streamlit secrets
    BASE_URL = st.secrets.get("BASE_URL")
    API_KEY = st.secrets.get("API_KEY")
    MODEL_NAME = st.secrets.get("MODEL_NAME")
    GOOGLE_CREDS_JSON = st.secrets.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")

    if not all([API_KEY, MODEL_NAME, GOOGLE_CREDS_JSON]):
        st.error("Error: Missing required secrets. Please check your Streamlit secrets configuration.")
        sys.exit(1)

    # Configure Google AI
    configure(api_key=API_KEY)
    
    # Initialize the model
    model = genai.GenerativeModel(MODEL_NAME)

    # Configure the model settings
    config = RunConfig(
        model=model,
        temperature=0.7,
        max_tokens=1000,
        tracing_disabled=True
    )

except Exception as e:
    st.error(f"Error initializing Google AI client: {str(e)}")
    sys.exit(1)
