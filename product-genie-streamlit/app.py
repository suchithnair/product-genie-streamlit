import streamlit as st
import requests
import os

# --- CONFIG ---
DATABRICKS_URL = os.getenv(
    "DATABRICKS_ENDPOINT",
    "https://dbc-99bad568-66d0.cloud.databricks.com/serving-endpoints/product-semantic-search-model-endpoint/invocations"
)
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "dapi2918bbae58f302b0562e433d822c737d")

headers = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json",
}

# --- STREAMLIT PAGE ---
st.set_page_config(page_title="ProductGenie", page_icon="🤖", layout="wide")
st.title("💬 Product Genie")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CHAT INPUT ---
query = st.chat_input("Type your query (e.g., 'I am going for hiking in New York in January')")

if query:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": query})

    # Prepare payload
    payload = {
        "dataframe_split": {
            "columns": ["query"],
            "data": [[query]]
        }
    }

    try:
        # Call Databricks endpoint
        response = requests.post(DATABRICKS_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # Parse predictions
        results = data.get("predictions", [])[0].get("results", [])
        st.session_state.messages.append({"role": "assistant", "content": results})

    except Exception as e:
        st.error(f"Error: {e}")

# --- DISPLAY CHAT ---
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    else:
        with st.chat_message("assistant"):
            results = msg["content"]
            if isinstance(results, list):
                for item in results:
                    with st.container():
                        st.markdown(
                            f"""
                            <div style="
                                border: 1px solid #ddd;
                                border-radius: 12px;
                                padding: 16px;
                                margin-bottom: 12px;
                                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                            ">
                                <h4 style="margin:0;">{item.get("title","(No Title)")}</h4>
                                <p style="color:gray; margin:0;">Store: {item.get("store","N/A")}</p>
                                <p style="margin-top:8px;">{item.get("description","")[:250]}...</p>
                                <p><b>Rating:</b> ⭐ {round(item.get("average_rating",0),1)} | 
                                   <b>Score:</b> {round(item.get("score",0),3)}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
            else:
                st.write(results)
