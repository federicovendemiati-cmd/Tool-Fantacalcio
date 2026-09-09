import streamlit as st

st.title("⚽ Tool Fantacalcio")
st.write("Benvenuto nel tuo assistente per l'asta in tempo reale!")

giocatore = st.text_input("Cerca un giocatore:")
if giocatore:
    st.write(f"Hai cercato: {giocatore}")
