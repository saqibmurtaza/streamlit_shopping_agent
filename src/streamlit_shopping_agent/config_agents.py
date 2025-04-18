from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, function_tool, set_tracing_disabled
from agents.run import RunConfig
from dotenv import load_dotenv
import os, asyncio

# Load environment variables
load_dotenv()

BASE_URL = os.getenv('BASE_URL') or ""
API_KEY = os.getenv('API_KEY') or ""
MODEL_NAME = os.getenv('MODEL_NAME') or ""

client = AsyncOpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

set_tracing_disabled(disabled=True)


model = OpenAIChatCompletionsModel(
    model=MODEL_NAME,
    openai_client=client
)

config= RunConfig(
    model=model,
    model_provider=client,
    tracing_disabled=True,
)
