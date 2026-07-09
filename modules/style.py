import streamlit as st

def load_css():

    st.markdown("""
    <style>

    body {
        background-color: #f5f5f5;
    }

    </style>
    """, unsafe_allow_html=True)