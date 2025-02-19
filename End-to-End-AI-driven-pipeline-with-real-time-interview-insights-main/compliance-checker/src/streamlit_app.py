import streamlit as st
import pandas as pd
import os
from PyPDF2 import PdfReader
from docx import Document

DB_PATH = "indian_health_chatbot_dataset.xlsx"  # Ensure this path is correct

def load_database():
    try:
        if os.path.exists(DB_PATH):
            df = pd.read_excel(DB_PATH)
            st.success("Database loaded successfully!")
            return df
        else:
            st.warning("Database not found! Please upload a dataset.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading database: {e}")
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
        response = generate_response(user_input, database)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.sidebar.chat_message("user").markdown(user_input)
        st.sidebar.chat_message("assistant").markdown(response)

def generate_response(user_input, database):
    if database.empty:
        return "I'm here to help, but I don't have any data to reference yet! Please upload a dataset."
    
    matched_rows = database[database.apply(lambda row: user_input.lower() in row.astype(str).str.lower().to_string(), axis=1)]
    if not matched_rows.empty:
        return matched_rows.iloc[0].to_string()
    else:
        return "I couldn't find relevant data in the database. Please try rephrasing your query."

def main():
    st.title("Med Assist: AI-Powered Diagnostic Assistance and Chatbot")
    
    st.sidebar.header("Navigation")
    options = st.sidebar.radio("Select a page:", ["Home", "Data Upload", "Database", "About"])
    
    database = load_database()
    chatbot(database)
    
    if options == "Home":
        st.header("Welcome to Med Assist")
        st.write("This app provides AI-powered health insights and chatbot support for medical queries.")
    
    elif options == "Data Upload":
        st.header("Upload New Data")
        new_data = upload_data()
        if new_data is not None:
            st.session_state.new_data = new_data
    
    elif options == "Database":
        st.header("Database Overview")
        st.dataframe(database)
        
        if st.button("Save Uploaded Data to Database"):
            if 'new_data' in st.session_state and isinstance(st.session_state.new_data, pd.DataFrame):
                updated_database = pd.concat([database, st.session_state.new_data], ignore_index=True)
                save_database(updated_database)
            else:
                st.warning("No new data available to save!")
    
    elif options == "About":
        st.header("About This App")
        st.write("Med Assist is an AI-powered chatbot designed to provide medical support using a preloaded dataset. It can analyze health conditions, offer recommendations, and help users understand medical information.")

if __name__ == "__main__":
    main()
