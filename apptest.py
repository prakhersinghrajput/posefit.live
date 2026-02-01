import streamlit as st
import mediapipe as mp

st.title("MediaPipe Test")

st.write("MediaPipe version:", mp.__version__)
st.success("MediaPipe imported successfully!")
