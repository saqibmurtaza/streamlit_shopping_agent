import streamlit as st
from openai import AssistantEventHandler, OpenAI
from openai_agent_sdk.agent import Agent
from openai_agent_sdk.models import ChatMessage
from agents.search_products import search_products
import json

# --- Setup session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "cart" not in st.session_state:
    st.session_state.cart = []

# --- Initialize OpenAI and Agent ---
openai_client = OpenAI()
agent = Agent(
    llm=openai_client,
    tools=[search_products],
    system_message="""
    You are a helpful furniture shopping assistant.
    - Use the `search_products` tool to help users find products.
    - When users express interest in a product, show basic details.
    - When users say things like 'add to cart', extract the product name and confirm.
    - Always be polite, conversational, and concise.
    """
)

# --- Title ---
st.set_page_config(page_title="Furniture Assistant", page_icon="🪑")
st.title("🪑 Furniture Shopping Assistant")

# --- Chat input ---
user_input = st.chat_input("Ask about a product...")
if user_input:
    st.session_state.chat_history.append(ChatMessage(role="user", content=user_input))
    with st.spinner("Thinking..."):
        response = agent.run(messages=st.session_state.chat_history)

        # Append assistant's full response to history
        st.session_state.chat_history.append(ChatMessage(role="assistant", content=response))

        # --- Add to cart detection ---
        if "add to cart" in user_input.lower():
            for product in json.loads(response).get("products", []):
                st.session_state.cart.append({
                    "name": product.get("name", "Unknown"),
                    "price": product.get("price", "0")
                })
                st.toast(f"✅ Added {product['name']} to cart")

# --- Display chat messages ---
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
