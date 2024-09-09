import streamlit as st
import sqlite3
import random
import string
from datetime import datetime, timedelta
import configs as cfg


def create_api_keys_table_if_not_exists():
    conn = sqlite3.connect(cfg.DB_NAME, check_same_thread=False)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS api_keys (
                email TEXT,
                api_key_name TEXT,
                api_key TEXT,
                created_at TIMESTAMP
            )''')
    conn.commit()
    
# Function to generate a 32-character alphanumeric API key
def generate_api_key():
    return 'sk-user-' + ''.join(random.choices(string.ascii_letters + string.digits, k=32))

# Showing the API key first time
@st.dialog("You new API key")
def show_api_key_first_time(generated_api_key, api_key_name):
    st.markdown("### Please copy your API Key. API Key Name `{}`".format(api_key_name))
    st.code(generated_api_key)
    

# Function to create an API key
def create_api_key():
    st.subheader("Create API Key")
    api_key_name = st.text_input("API Key Name:")
    if st.button("Generate API Key"):
        if api_key_name:
            api_key = generate_api_key()
            created_at = datetime.now()
            conn = sqlite3.connect(cfg.DB_NAME, check_same_thread=False)
            c = conn.cursor()
            c.execute('INSERT INTO api_keys (email, api_key_name, api_key, created_at) VALUES (?, ?, ?, ?)', 
                      (st.session_state.email, api_key_name, api_key, created_at))
            conn.commit()
            show_api_key_first_time(api_key, api_key_name)
        else:
            st.warning("Please provide a name for the API key.")
            
            
# Function to delete an API key
def delete_api_key():
    st.subheader("Delete API Key")
    
    conn = sqlite3.connect(cfg.DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT api_key_name, api_key FROM api_keys WHERE email = ?', (st.session_state.email,))
    api_keys = c.fetchall()
    api_key_options = [f"{name} - {'*' * (len(key) - cfg.MASKED_API_KEY_LEN)}{key[-cfg.MASKED_API_KEY_LEN:]}" for name, key in api_keys]
    api_key_to_delete = st.selectbox("Select API Key to Delete:", api_key_options)
    
    if st.button("Delete API Key"):
        if api_key_to_delete:
            selected_name, selected_key = api_key_to_delete.split(" - ")
            selected_key = selected_key.replace('*', '')[-cfg.MASKED_API_KEY_LEN:]
            c.execute('DELETE FROM api_keys WHERE email = ? AND api_key_name = ? AND api_key LIKE ?', 
                      (st.session_state.email, selected_name, f"%{selected_key}"))
            conn.commit()
            st.success(f"API Key '{selected_name}' deleted successfully.")
        else:
            st.warning("Please select an API key to delete.")
            
            
# Function to display API keys
@st.fragment(run_every=5)
def display_api_keys():
    st.subheader("Your API Keys")
    
    conn = sqlite3.connect(cfg.DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT api_key_name, api_key, created_at FROM api_keys WHERE email = ?', (st.session_state.email,))
    rows = c.fetchall()
    if rows:
        table_md = "| API Key Name | Masked API Key | Creation Date |\n"
        table_md += "|--------------|----------------|---------------|\n"
        for row in rows:
            api_key_name, api_key, created_at = row
            masked_api_key = '*' * (len(api_key) - cfg.MASKED_API_KEY_LEN) + api_key[-cfg.MASKED_API_KEY_LEN:]  # Show only the last 4 characters of the API key
            table_md += f"| {api_key_name} | {masked_api_key} | {created_at} |\n"
        st.markdown(table_md)
    else:
        st.info("No API keys found.")
        
