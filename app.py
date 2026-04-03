import os
import streamlit as st
import replicate

# --- REPLICATE AUTHENTICATION FIX ---
# Priority 1: Streamlit Secrets (Recommended for Cloud)
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# Priority 2: Manual Sidebar Input (For debugging)
st.sidebar.subheader("API Configuration")
manual_token = st.sidebar.text_input("Replicate Token (r8_...)", type="password")
if manual_token:
    os.environ["REPLICATE_API_TOKEN"] = manual_token

# Check if it's working
current_token = os.environ.get("REPLICATE_API_TOKEN", "")
if not current_token:
    st.error("⚠️ No API Token found. Please add it to Streamlit Secrets or the sidebar.")
    st.stop()
elif not current_token.startswith("r8_"):
    st.error("❌ Invalid Token Format! Your token must start with 'r8_'.")
    st.stop()
# ------------------------------------
