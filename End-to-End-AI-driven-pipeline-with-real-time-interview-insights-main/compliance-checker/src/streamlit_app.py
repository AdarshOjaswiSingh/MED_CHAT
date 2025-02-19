import streamlit as st
import pandas as pd
import os
from PyPDF2 import PdfReader
from docx import Document
import re  # For text processing

DB_PATH = "End-to-End-AI-driven-pipeline-with-real-time-interview-insights-main/compliance-checker/src/Adarsh_Generated_Candidate_Data.xlsx"

# Load database function
def load_database():
    try:
        if os.path.exists(DB_PATH):
            return pd.read_excel(DB_PATH)
        else:
            st.warning("Database not found! Initializing a new database.")
            empty_df = pd.DataFrame(columns=["ID", "Name", "Email", "Summary", "Keywords"])  # Structured format
            save_database(empty_df)
            return empty_df
    except Exception as e:
        st.error(f"Failed to load database: {e}")
        return pd.DataFrame()

# Save database function
def save_database(data):
    try:
        data.to_excel(DB_PATH, index=False)
        st.success("Database updated successfully!")
    except Exception as e:
        st.error(f"Failed to save the database: {e}")

# Extract text from PDF
def extract_pdf_text(file):
    try:
        reader = PdfReader(file)
        text = '\n'.join([page.extract_text() for page in reader.pages if page.extract_text()])
        return extract_structured_data(text)
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

# Extract text from Word documents
def extract_word_text(file):
    try:
        doc = Document(file)
        text = '\n'.join([para.text for para in doc.paragraphs])
        return extract_structured_data(text)
    except Exception as e:
        st.error(f"Error reading Word document: {e}")
        return ""

# Extract key structured data
def extract_structured_data(text):
    try:
        email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        email = email_match.group() if email_match else "Not found"

        # Example: Extracting a name (Assumes first two words are name)
        words = text.split()
        name = " ".join(words[:2]) if len(words) > 1 else "Unknown"

        # Extract keywords (Basic NLP)
        keywords = ', '.join(set(re.findall(r"\b[A-Za-z]{4,}\b", text)))  # Extract words > 4 characters

        summary = text[:500] + "..." if len(text) > 500 else text  # Short summary

        return {"Name": name, "Email": email, "Summary": summary, "Keywords": keywords}
    except Exception as e:
        st.error(f"Error processing structured data: {e}")
        return {"Name": "Unknown", "Email": "Not found", "Summary": "", "Keywords": ""}

# Upload data and extract structured insights
def upload_data():
    uploaded_file = st.file_uploader("Upload a file (CSV, PDF, or DOCX)", type=["csv", "pdf", "docx"])
    if uploaded_file:
        try:
            if uploaded_file.type == "text/csv":
                data = pd.read_csv(uploaded_file)
                st.dataframe(data)
                return data
            elif uploaded_file.type == "application/pdf":
                extracted_info = extract_pdf_text(uploaded_file)
                st.write(f"**Extracted Info:** {extracted_info}")
                return pd.DataFrame([extracted_info])
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                extracted_info = extract_word_text(uploaded_file)
                st.write(f"**Extracted Info:** {extracted_info}")
                return pd.DataFrame([extracted_info])
            else:
                st.error("Unsupported file type!")
        except Exception as e:
            st.error(f"Error processing file: {e}")
    return None

# Chatbot function
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
        response = "I'm here to help! How can I assist you?"  # Placeholder AI response
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.sidebar.chat_message("user").markdown(user_input)
        st.sidebar.chat_message("assistant").markdown(response)

# Main app function
def main():
    st.title("Med Assist: AI-Powered Diagnostic Assistance and Comfort Chatbot")
    st.sidebar.header("Navigation")
    options = st.sidebar.radio("Select a page:", ["Home", "Data Upload", "Database", "About"])
    
    chatbot()  # Calling chatbot function to add it to sidebar

    if options == "Home":
        st.header("Welcome to the Vit Project Dashboard")
        st.write("This app is designed to showcase the key features and outputs of our project.")
        st.write("Use the sidebar to navigate through the app.")
    
    elif options == "Data Upload":
        st.header("Upload New Data")
        new_data = upload_data()
        if new_data is not None:
            st.session_state.new_data = new_data

    elif options == "Database":
        st.header("Permanent Database")
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
        st.write("This app is an AI-powered mental health and medical support chatbot designed to assist users in managing their well-being through personalized recommendations, mood tracking, and interactive conversations. The chatbot provides mental health guidance, relaxation exercises, symptom analysis, and emotional support through both text and voice interactions.")
        st.write("Author: Adarsh Ojaswi Singh")

if __name__ == "__main__":
    main()
