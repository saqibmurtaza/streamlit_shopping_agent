import os, json, tempfile, sys, asyncio
import streamlit as st

# Setup Google credentials from Streamlit secrets
if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in st.secrets:
    try:
        # Get the credentials JSON string and ensure it's properly formatted
        creds_str = st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
        
        # Clean the string: remove any BOM and normalize newlines
        if isinstance(creds_str, str):
            creds_str = creds_str.encode('utf-8').decode('utf-8-sig')  # Remove BOM if present
            creds_str = creds_str.replace('\r\n', '\n').replace('\r', '\n')  # Normalize newlines
        
        # Create a temporary file for the credentials
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            if isinstance(creds_str, dict):
                json.dump(creds_str, f, indent=2)
            else:
                # If it's a string, parse it first then dump it
                creds_dict = json.loads(creds_str)
                json.dump(creds_dict, f, indent=2)
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f.name
    except json.JSONDecodeError as e:
        st.error(f"Error parsing Google credentials JSON: {str(e)}")
        st.error("Please ensure your Google credentials are properly formatted JSON")
    except Exception as e:
        st.error(f"Error setting up Google credentials: {str(e)}")

# Add src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

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
if user_input:
    # Add user message to chat history
    st.session_state.chat_history.append(ChatMessage(role="user", content=user_input))
    
    # Format chat history for the agent
    formatted_chat_history = [
        {"role": msg.role, "content": msg.content if isinstance(msg.content, str) else json.dumps(msg.content)}
        for msg in st.session_state.chat_history
    ]

    with st.spinner("Thinking..."):
        try:
            # Get response from agent
            response = asyncio.run(
                Runner.run(
                    shopping_manager,
                    formatted_chat_history
                )
            )
            
            # Parse the response if it's a string containing JSON
            if isinstance(response, str):
                try:
                    response_data = json.loads(response)
                except json.JSONDecodeError:
                    response_data = {"role": "assistant", "content": response}
            else:
                response_data = response

            # Add assistant message to chat history
            st.session_state.chat_history.append(
                ChatMessage(
                    role="assistant",
                    content=response_data.get("content", response)
                )
            )
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.chat_history.append(
                ChatMessage(role="assistant", content=f"I apologize, but I encountered an error: {str(e)}")
            )

# --- Display chat messages ---
for msg in st.session_state.chat_history:
    with st.chat_message(msg.role):
        if isinstance(msg.content, dict):
            # Display structured content
            if "products" in msg.content:
                st.write(msg.content["message"])
                if msg.content["products"]:
                    st.write("Found Products:")
                    for product in msg.content["products"]:
                        st.write(f"- {product['name']} (${product['price']})")
                if msg.content["recommended_products"]:
                    st.write("Recommended Products:")
                    for product in msg.content["recommended_products"]:
                        st.write(f"- {product['name']} (${product['price']})")
        else:
            # Display regular message content
            st.markdown(str(msg.content))

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

# --- Clear buttons ---
with st.sidebar:
    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()
    if st.button("🗑️ Clear Cart"):
        st.session_state.cart = []
        st.rerun()


