import streamlit as st
import pandas as pd
import os
from PyPDF2 import PdfReader
from docx import Document

# Set database path
DB_PATH = "End-to-End-AI-driven-pipeline-with-real-time-interview-insights-main/compliance-checker/src/indian_health_chatbot_dataset.xlsx"

def load_database():
    """Loads the dataset from the given path."""
    if os.path.exists(DB_PATH):
        return pd.read_excel(DB_PATH)
    else:
        st.warning("Database not found! Please upload a dataset.")
        return pd.DataFrame()

def save_database(data):
    """Saves data to the database."""
    try:
        data.to_excel(DB_PATH, index=False)
        st.success("Database updated successfully!")
    except Exception as e:
        st.error(f"Failed to save the database: {e}")

def extract_pdf_text(file):
    """Extracts text from a PDF file."""
    try:
        reader = PdfReader(file)
        return '\n'.join([page.extract_text() for page in reader.pages if page.extract_text()])
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def extract_word_text(file):
    """Extracts text from a Word document."""
    try:
        doc = Document(file)
        return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"Error reading Word document: {e}")
        return ""

def upload_data():
    """Handles file uploads and extracts content."""
    uploaded_file = st.file_uploader("Upload a file (CSV, PDF, or DOCX)", type=["csv", "pdf", "docx"])
    if uploaded_file:
        try:
            if uploaded_file.type == "text/csv":
                data = pd.read_csv(uploaded_file)
                st.dataframe(data)
                return data
            elif uploaded_file.type == "application/pdf":
                text = extract_pdf_text(uploaded_file)
                st.text_area("Extracted PDF Content", text, height=300)
                return text
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = extract_word_text(uploaded_file)
                st.text_area("Extracted Word Content", text, height=300)
                return text
            else:
                st.error("Unsupported file type!")
        except Exception as e:
            st.error(f"Error processing file: {e}")
    return None

def chatbot():
    """Chatbot functionality using dataset."""
    st.sidebar.header("AI Chatbot Assistant")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    db = load_database()
    
    for message in st.session_state.chat_history:
        with st.sidebar.chat_message(message["role"]):
            st.markdown(message["content"])
    
    user_input = st.sidebar.chat_input("Ask something about health...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Search dataset for related responses
        response = "I couldn't find relevant information. Please rephrase your query."
        if not db.empty:
            matched_responses = db[db.apply(lambda row: row.astype(str).str.contains(user_input, case=False, na=False).any(), axis=1)]
            if not matched_responses.empty:
                response = matched_responses.sample(1).to_string(index=False)
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.sidebar.chat_message("user").markdown(user_input)
        st.sidebar.chat_message("assistant").markdown(response)

def main():
    """Main function for Streamlit app."""
    st.title("Med Assist: AI-Powered Diagnostic Assistance and Chatbot")
    st.sidebar.header("Navigation")
    options = st.sidebar.radio("Select a page:", ["Home", "Data Upload", "Database", "About"])
    
    chatbot()
    
    if options == "Home":
        st.header("Welcome to the AI Health Assistant")
        st.write("Ask health-related questions and get AI-powered responses.")
    elif options == "Data Upload":
        st.header("Upload New Data")
        new_data = upload_data()
        if new_data is not None:
            st.session_state.new_data = new_data
    elif options == "Database":
        st.header("Database Overview")
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
        st.write("This AI chatbot assists users with health-related inquiries using a dataset of common medical queries and responses.")
        st.write("Author: Adarsh Ojaswi Singh")

if __name__ == "__main__":
    main()
