import streamlit as st
import pandas as pd
import os
from PyPDF2 import PdfReader
from docx import Document

# Path to the dataset
dataset_path = "End-to-End-AI-driven-pipeline-with-real-time-interview-insights-main/compliance-checker/src/indian_health_chatbot_dataset.xlsx"

def load_database():
    try:
        if os.path.exists(dataset_path):
            return pd.read_excel(dataset_path)
        else:
            st.warning("Database not found! Please upload a dataset.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to load database: {e}")
        return pd.DataFrame()

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
        return '\n'.join([para.text for para in doc.paragraphs if para.text])
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
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    for message in st.session_state.chat_history:
        with st.sidebar.chat_message(message["role"]):
            st.markdown(message["content"])
    
    user_input = st.sidebar.chat_input("Ask something...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        database = load_database()
        
        if not database.empty:
            response = "No relevant information found."
            for _, row in database.iterrows():
                if any(keyword in user_input.lower() for keyword in row["Keywords"].lower().split(", ")):
                    response = f"{row['Name']} has asked a similar question before. Here's some insight: {row['Summary']}"
                    break
        else:
            response = "I'm here to help! How can I assist you?"
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.sidebar.chat_message("user").markdown(user_input)
        st.sidebar.chat_message("assistant").markdown(response)

def main():
    st.title("Med Assist: AI-Powered Diagnostic Assistance and Comfort Chatbot")
    st.sidebar.header("Navigation")
    options = st.sidebar.radio("Select a page:", ["Home", "Data Upload", "Database", "Chatbot", "About"])
    
    if options == "Home":
        st.header("Welcome to Med Assist Dashboard")
        st.write("This AI-powered chatbot helps in mental health and medical support.")
    
    elif options == "Data Upload":
        st.header("Upload New Data")
        new_data = upload_data()
        if new_data is not None:
            st.session_state.new_data = new_data
    
    elif options == "Database":
        st.header("Dataset Viewer")
        database = load_database()
        st.dataframe(database)
    
    elif options == "Chatbot":
        chatbot()
    
    elif options == "About":
        st.header("About This App")
        st.write("This chatbot provides mental health and medical assistance using AI-driven recommendations.")
        st.write("Author: Adarsh Ojaswi Singh")

if __name__ == "__main__":
    main()
