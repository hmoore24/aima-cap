import streamlit as st
import openai
from openai import OpenAI

st.write("Key loaded:", "OPENAI_API_KEY" in st.secrets)
