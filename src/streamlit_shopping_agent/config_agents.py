from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, set_tracing_disabled
from agents.run import RunConfig
import streamlit as st
import sys

try:
    # Get configuration from Streamlit secrets
    API_KEY = st.secrets.get("API_KEY")
    MODEL_NAME = st.secrets.get("MODEL_NAME", "gpt-3.5-turbo")
    GOOGLE_CREDS_JSON = st.secrets.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")

    if not API_KEY:
        st.error("Error: Missing API key. Please check your Streamlit secrets configuration.")
        sys.exit(1)

    # Initialize OpenAI client
    client = AsyncOpenAI(
        api_key=API_KEY,
        base_url="https://api.openai.com/v1"  # Default OpenAI API URL
    )

    set_tracing_disabled(disabled=True)

    # Initialize the model without temperature parameter
    model = OpenAIChatCompletionsModel(
        model=MODEL_NAME,
        openai_client=client
    )

    # Configure the model settings
    config = RunConfig(
        model=model,
        model_provider=client,
        tracing_disabled=True
    )

except Exception as e:
    st.error(f"Error initializing OpenAI client: {str(e)}")
    sys.exit(1)
