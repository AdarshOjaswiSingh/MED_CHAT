import streamlit as st
import pandas as pd
import os
from PyPDF2 import PdfReader
from docx import Document

# File paths
DB_PATH = "chatbot_dataset.csv"

def load_database():
    if os.path.exists(DB_PATH):
        return pd.read_csv(DB_PATH)
    else:
        st.warning("Database not found! Initializing a new database.")
        empty_df = pd.DataFrame(columns=["User", "Mood", "Interaction", "Response", "Recommendation"])
        save_database(empty_df)
        return empty_df

def save_database(data):
    data.to_csv(DB_PATH, index=False)
    st.success("Database updated successfully!")

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
    uploaded_file = st.file_uploader("Upload a file (CSV, PDF, DOCX)", type=["csv", "pdf", "docx"])
    if uploaded_file:
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
        
        # Fetch relevant response based on dataset
        mood_responses = database[database["Mood"].str.contains(user_input, case=False, na=False)]
        if not mood_responses.empty:
            response = mood_responses.iloc[0]["Response"]
        else:
            response = "I'm here to help! How can I assist you?"
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.sidebar.chat_message("user").markdown(user_input)
        st.sidebar.chat_message("assistant").markdown(response)

def main():
    st.title("Med Assist: AI-Powered Diagnostic Assistance and Comfort Chatbot")
    st.sidebar.header("Navigation")
    options = st.sidebar.radio("Select a page:", ["Home", "Data Upload", "Database", "About"])
    
    chatbot()
    
    if options == "Home":
        st.header("Welcome to Med Assist Dashboard")
        st.write("Use the sidebar to navigate through the app.")
    
    elif options == "Data Upload":
        st.header("Upload New Data")
        new_data = upload_data()
        if new_data is not None:
            st.session_state.new_data = new_data

    elif options == "Database":
        st.header("Dataset")
        database = load_database()
        st.dataframe(database)
        
        if st.button("Save Uploaded Data to Database"):
            if 'new_data' in st.session_state and isinstance(st.session_state.new_data, pd.DataFrame):
                updated_database = pd.concat([database, st.session_state.new_data], ignore_index=True)
                save_database(updated_database)
            else:
                st.warning("No new data available to save!")

    elif options == "About":
        st.header("About This App")
        st.write("AI-powered mental health chatbot providing personalized support.")
        st.write("Author: Adarsh Ojaswi Singh")

if __name__ == "__main__":
    main()
