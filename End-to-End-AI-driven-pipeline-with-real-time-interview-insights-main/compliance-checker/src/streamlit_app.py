import streamlit as st
import pandas as pd
import os
from PyPDF2 import PdfReader
from docx import Document
from fuzzywuzzy import process

DB_PATH = "End-to-End-AI-driven-pipeline-with-real-time-interview-insights-main/compliance-checker/src/indian_health_chatbot_dataset.xlsx"

def load_database():
    try:
        if os.path.exists(DB_PATH):
            return pd.read_excel(DB_PATH)
        else:
            st.warning("Database not found! Please upload a dataset.")
            return pd.DataFrame(columns=["Question", "Response"])
    except Exception as e:
        st.error(f"Failed to load database: {e}")
        return pd.DataFrame(columns=["Question", "Response"])

def save_database(data):
    try:
        data.to_excel(DB_PATH, index=False)
        st.success("Database updated successfully!")
    except Exception as e:
        st.error(f"Failed to save the database: {e}")

def extract_pdf_text(file):
    try:
        reader = PdfReader(file)
        return '\n'.join([page.extract_text() for page in reader.pages if page.extract_text()])
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
                save_database(data)
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

def chatbot(database):
    st.sidebar.header("Chatbot Assistant")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    for message in st.session_state.chat_history:
        with st.sidebar.chat_message(message["role"]):
            st.markdown(message["content"])
    
    user_input = st.sidebar.chat_input("Ask something...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        response = get_chatbot_response(user_input, database)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.sidebar.chat_message("user").markdown(user_input)
        st.sidebar.chat_message("assistant").markdown(response)

def get_chatbot_response(user_input, database):
    greetings = ["hi", "hello", "hey", "greetings", "good morning", "good evening", "namaste"]
    
    if user_input.lower() in greetings:
        return "Hello! How can I assist you today?"
    
    if not database.empty:
        questions = database["Question"].dropna().tolist()
        if questions:
            best_match, score = process.extractOne(user_input, questions)
            if score > 60:
                response = database.loc[database["Question"] == best_match, "Response"].values[0]
                return response
    
    return "I'm here to help, but I couldn't find relevant data. Can you provide more details?"

def main():
    st.title("Med Assist: AI-Powered Diagnostic Assistance and Comfort Chatbot")
    st.sidebar.header("Navigation")
    options = st.sidebar.radio("Select a page:", ["Home", "Data Upload", "Database", "About"])
    
    database = load_database()
    chatbot(database)

    if options == "Home":
        st.header("Welcome to the Med Assist Dashboard")
        st.write("This app is designed to provide AI-powered diagnostic assistance and chatbot interactions.")
    
    elif options == "Data Upload":
        st.header("Upload New Data")
        new_data = upload_data()
        if new_data is not None:
            st.session_state.new_data = new_data
    
    elif options == "Database":
        st.header("Database Overview")
        if database.empty:
            st.warning("Database not found! Please upload a dataset.")
        else:
            st.dataframe(database)
    
    elif options == "About":
        st.header("About This App")
        st.write("This chatbot assists users in managing their well-being with AI-driven recommendations.")

if __name__ == "__main__":
    main()
