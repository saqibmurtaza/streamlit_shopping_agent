import os, json, tempfile, sys, asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Handle Google credentials if available
gc_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if gc_json:
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(gc_json)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f.name

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Add src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

import streamlit as st
from streamlit_shopping_agent.models import ChatMessage
from streamlit_shopping_agent.tools import search_products
from streamlit_shopping_agent.config_agents import config
from streamlit_shopping_agent.shopping_agents import shopping_manager
from agents import Runner

# --- Setup session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "cart" not in st.session_state:
    st.session_state.cart = []

# --- Title ---
st.set_page_config(page_title="Furniture Assistant", page_icon="🪑")
st.title("🪑 Furniture Shopping Assistant")

# --- Chat input ---
user_input = st.chat_input("Ask about a product...")

# Convert chat history to the expected format before passing to Runner.run
formatted_chat_history = [
    {"role": msg.role, "content": msg.content} for msg in st.session_state.chat_history
]

# Ensure the response from Runner.run is converted to a string before appending to chat_history
if user_input:
    st.session_state.chat_history.append(ChatMessage(role="user", content=user_input))
    with st.spinner("Thinking..."):
        response = asyncio.run(
            Runner.run(
                shopping_manager,
                formatted_chat_history
            )
        )

        # Convert response to string if it's not already
        response_content = str(response) if not isinstance(response, str) else response

        st.session_state.chat_history.append(ChatMessage(role="assistant", content=response_content))

# --- Display chat messages ---#
for msg in st.session_state.chat_history:
    with st.chat_message(msg.role):
        st.markdown(msg.content)

# --- Cart sidebar ---
st.sidebar.title("🛒 Your Cart")
if st.session_state.cart:
    total = 0
    for item in st.session_state.cart:
        st.sidebar.markdown(f"- **{item['name']}** (${item['price']})")
        try:
            total += float(item['price'])
        except:
            pass
    st.sidebar.markdown(f"**Total:** ${total:.2f}")
else:
    st.sidebar.markdown("Cart is empty.")

# --- Add to cart detection ---
if st.session_state.chat_history:
    last_msg = st.session_state.chat_history[-1].content.lower()
    if "add to cart" in last_msg:
        added = False
        for msg in reversed(st.session_state.chat_history):
            if msg.role == "assistant":
                lines = msg.content.split("\n")
                for line in lines:
                    if line.startswith("- "):
                        product_name = line.strip("- ").strip()
                        st.session_state.cart.append({"name": product_name, "price": "Unknown"})
                        added = True
                        break
                    if added:
                        break
                    if not added:
                        st.sidebar.warning("Couldn't identify the product to add to cart.")

# --- Optional: Button to clear chat or cart ---
with st.sidebar:
    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()
    if st.button("🗑️ Clear Cart"):
        st.session_state.cart = []
        st.rerun()

# if st.button("🗑️ Clear Cart"):
#         st.session_state.cart = []
#         st.rerun()
