import streamlit as st
import pandas as pd
import os
from PyPDF2 import PdfReader
from docx import Document

DB_PATH = "indian_health_chatbot_dataset.xlsx"

def load_database():
    try:
        if os.path.exists(DB_PATH):
            return pd.read_excel(DB_PATH)
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
        return '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
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
        response = search_database(database, user_input)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.sidebar.chat_message("user").markdown(user_input)
        st.sidebar.chat_message("assistant").markdown(response)

def search_database(database, query):
    if database.empty:
        return "Database not found! Please upload a dataset."
    
    results = database[database.apply(lambda row: row.astype(str).str.contains(query, case=False, na=False).any(), axis=1)]
    if not results.empty:
        return results.iloc[0].to_dict()
    else:
        return "I couldn't find relevant data in the database. Please try rephrasing your query."

def main():
    st.title("Med Assist: AI-Powered Diagnostic Assistance and Chatbot")
    st.sidebar.header("Navigation")
    options = st.sidebar.radio("Select a page:", ["Home", "Data Upload", "Database", "About"])
    
    database = load_database()
    chatbot(database)
    
    if options == "Home":
        st.header("Welcome to the Med Assist Dashboard")
        st.write("This app provides AI-powered healthcare guidance and chatbot support based on an Indian health dataset.")
    
    elif options == "Data Upload":
        st.header("Upload New Data")
        new_data = upload_data()
        if new_data is not None:
            st.session_state.new_data = new_data
    
    elif options == "Database":
        st.header("Database Overview")
        st.dataframe(database)
    
    elif options == "About":
        st.header("About This App")
        st.write("Med Assist is an AI-driven chatbot designed to assist with health-related queries using a dataset focused on Indian healthcare.")

if __name__ == "__main__":
    main()
