import streamlit as st
import pandas as pd
import os
from PyPDF2 import PdfReader
from docx import Document
from llama_cpp import Llama  # Import LLaMA 2 model

# --- CONFIGURATIONS ---
DB_PATH = "Adarsh_Generated_Candidate_Data.xlsx"  # Ensure this file exists
MODEL_PATH = r"C:\Users\adars\Downloads\iiiiooooo\jjjjjjjjjjj\llama-2-7b.Q2_K.gguf"  # Update your LLaMA 2 path

# Load LLaMA 2 model
@st.cache_resource
def load_llama_model():
    return Llama(model_path=MODEL_PATH, n_ctx=2048)

llm = load_llama_model()

# --- DATABASE HANDLING ---
def load_database():
    """Loads or initializes the database."""
    try:
        if os.path.exists(DB_PATH):
            return pd.read_excel(DB_PATH)
        else:
            st.warning("Database not found! Initializing a new one.")
            empty_df = pd.DataFrame(columns=["Column1", "Column2", "Column3"])  # Customize as needed
            save_database(empty_df)
            return empty_df
    except Exception as e:
        st.error(f"Failed to load database: {e}")
        return pd.DataFrame()

def save_database(data):
    """Saves the database to an Excel file."""
    try:
        data.to_excel(DB_PATH, index=False)
        st.success("Database updated successfully!")
    except Exception as e:
        st.error(f"Failed to save the database: {e}")

# --- FILE HANDLING ---
def extract_pdf_text(file):
    """Extracts text from a PDF file."""
    try:
        reader = PdfReader(file)
        return ''.join([page.extract_text() for page in reader.pages if page.extract_text()])
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
    """Handles file uploads (CSV, PDF, DOCX)."""
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

# --- AI CHATBOT USING LLaMA 2 ---
def chatbot():
    """Integrates LLaMA 2 chatbot into the sidebar."""
    st.sidebar.header("🤖 AI Chatbot Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        with st.sidebar.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.sidebar.chat_input("Ask something...")
    
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Generate response from LLaMA 2
        with st.spinner("Thinking..."):
            response = llm(f"User: {user_input}\nAI:", max_tokens=200)
        
        assistant_reply = response["choices"][0]["text"].strip() if "choices" in response else "I'm here to help!"
        
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
        
        # Display chat messages
        st.sidebar.chat_message("user").markdown(user_input)
        st.sidebar.chat_message("assistant").markdown(assistant_reply)

# --- MAIN APP ---
def main():
    st.title("🩺 Med Assist: AI-Powered Diagnostic Assistant & Chatbot")
    st.sidebar.header("📌 Navigation")
    options = st.sidebar.radio("Select a page:", ["🏠 Home", "📂 Data Upload", "📊 Database", "ℹ️ About"])

    chatbot()  # Call chatbot in sidebar

    if options == "🏠 Home":
        st.header("Welcome to Med Assist!")
        st.write("This AI-powered app provides **diagnostic assistance, mental health support, and chatbot interactions**.")
        st.write("Use the sidebar to navigate through different features.")

    elif options == "📂 Data Upload":
        st.header("Upload Your Data")
        new_data = upload_data()
        if new_data is not None:
            st.session_state.new_data = new_data

    elif options == "📊 Database":
        st.header("📁 Permanent Database")
        database = load_database()
        st.dataframe(database)

        if st.button("Save Uploaded Data to Database"):
            if 'new_data' in st.session_state and isinstance(st.session_state.new_data, pd.DataFrame):
                updated_database = pd.concat([database, st.session_state.new_data], ignore_index=True)
                save_database(updated_database)
            else:
                st.warning("No new data available to save!")

    elif options == "ℹ️ About":
        st.header("ℹ️ About Med Assist")
        st.write("Med Assist is an AI-powered chatbot designed for **mental health support and medical assistance**.")
        st.write("It provides **personalized recommendations, symptom analysis, and relaxation exercises**.")
        st.write("💡 Developed by **Adarsh Ojaswi Singh**.")

if __name__ == "__main__":
    main()
