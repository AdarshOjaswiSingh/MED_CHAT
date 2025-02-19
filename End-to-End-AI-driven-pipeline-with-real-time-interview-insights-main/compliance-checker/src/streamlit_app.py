import streamlit as st
import pandas as pd
import os
from PyPDF2 import PdfReader
from docx import Document

DB_PATH = "End-to-End-AI-driven-pipeline-with-real-time-interview-insights-main/compliance-checker/src/chatbot_dataset.xlsx"

def load_database():
    try:
        if os.path.exists(DB_PATH):
            return pd.read_excel(DB_PATH)
        else:
            st.warning("Database not found! Initializing with sample data.")
            sample_data = pd.DataFrame({
                "User_ID": [1, 2, 3, 4, 5],
                "User_Name": ["Alice", "Bob", "Charlie", "David", "Emma"],
                "Mood": ["Happy", "Stressed", "Sad", "Anxious", "Neutral"],
                "Last_Message": [
                    "I had a great day!",
                    "Work has been overwhelming.",
                    "Feeling down today.",
                    "I'm nervous about my exam.",
                    "Just a regular day."
                ],
                "AI_Response": [
                    "That's awesome! Keep up the positive energy! 😊",
                    "Take a deep breath. Maybe a short break will help. 🌿",
                    "I'm here for you. Want to talk about it? 💙",
                    "Try some deep breathing exercises. You got this! ✨",
                    "Let me know if you need anything. I'm here to chat!"
                ]
            })
            save_database(sample_data)
            return sample_data
    except Exception as e:
        st.error(f"Failed to load database: {e}")
        return pd.DataFrame()

def save_database(data):
    try:
        data.to_excel(DB_PATH, index=False)
        st.success("Database updated successfully!")
    except Exception as e:
        st.error(f"Failed to save the database: {e}")
def extract_pdf_text(file):
    try:
        reader = PdfReader(file)
        return ''.join([page.extract_text() for page in reader.pages])
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def extract_word_text(file):
    try:
        doc = Document(file)
        return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"Error reading Word document: {e}")
        return ""

def upload_data():
    uploaded_file = st.file_uploader("Upload a file (CSV, PDF, or DOCX)", type=["csv", "pdf", "docx"])
    if uploaded_file:
        try:
            if uploaded_file.type == "text/csv":
                data = pd.read_csv(uploaded_file)
                st.dataframe(data)
                return data
            elif uploaded_file.type == "application/pdf":
                text = extract_pdf_text(uploaded_file)
                st.text_area("PDF Content", text, height=300)
                return text
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = extract_word_text(uploaded_file)
                st.text_area("Word Content", text, height=300)
                return text
            else:
                st.error("Unsupported file type!")
        except Exception as e:
            st.error(f"Error processing file: {e}")
    return None


def chatbot():
    st.sidebar.header("Chatbot Assistant")
    database = load_database()
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    for message in st.session_state.chat_history:
        with st.sidebar.chat_message(message["role"]):
            st.markdown(message["content"])
    
    user_input = st.sidebar.chat_input("Ask something...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        response = database.loc[database['Last_Message'] == user_input, 'AI_Response']
        response = response.iloc[0] if not response.empty else "I'm here to help! How can I assist you?"
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.sidebar.chat_message("user").markdown(user_input)
        st.sidebar.chat_message("assistant").markdown(response)

def main():
    st.title("Med Assist: AI-Powered Diagnostic Assistance and Comfort Chatbot")
    st.sidebar.header("Navigation")
    options = st.sidebar.radio("Select a page:", ["Home", "Database", "About"])
    
    chatbot()
    
    if options == "Home":
        st.header("Welcome to the Med Assist Dashboard")
        st.write("This AI-powered chatbot provides mental health guidance, symptom analysis, and emotional support.")
    
    elif options == "Database":
        st.header("Chatbot Database")
        database = load_database()
        st.dataframe(database)
    
    elif options == "About":
        st.header("About This App")
        st.write("This app is designed to assist users in managing their mental well-being through personalized recommendations and interactive conversations.")
        st.write("Author: Adarsh Ojaswi Singh")

if __name__ == "__main__":
    main()
