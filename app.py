import os
import sys

import streamlit as st

from auths import (
    create_users_table_if_not_exists,
    log_in_mechanism,
    log_out_mechanism
)

from api_key_backend import (
    create_api_keys_table_if_not_exists,
    create_api_key,
    delete_api_key,
    display_api_keys
)
    
# Initialize auth session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = ''



# Main application logic
def main():
    st.title("Your custom application")

    if st.session_state.logged_in:
        # Application logic!!
        st.sidebar.success(f"Welcome, {st.session_state.email}!")
        
        # API Keys
        display_api_keys()
        create_api_key()
        delete_api_key()
        
        # When user clicks on log out button
        log_out_mechanism()
    else:
        # When user logs in
        log_in_mechanism()
                
                
if __name__ == "__main__":
    create_users_table_if_not_exists()
    create_api_keys_table_if_not_exists()
    main()
