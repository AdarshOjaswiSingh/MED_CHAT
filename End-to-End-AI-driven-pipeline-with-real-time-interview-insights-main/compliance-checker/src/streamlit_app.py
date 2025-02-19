import streamlit as st
import pandas as pd
import os
from PyPDF2 import PdfReader
from docx import Document
from llama_cpp import Llama
import openai

# ===================== CONFIGURATION ===================== #
DB_PATH = "End-to-End-AI-driven-pipeline-with-real-time-interview-insights-main/compliance-checker/src/Adarsh_Generated_Candidate_Data.xlsx"
MODEL_PATH = "C:/Users/adars/Downloads/iiiiooooo/jjjjjjjjjjj/llama-2-7b.Q2_K.gguf"  # LLaMA 2 model path
USE_OPENAI = False  # Set True to use OpenAI GPT instead

# Load LLaMA Model
llm = Llama(model_path=MODEL_PATH) if not USE_OPENAI else None

# ===================== DATABASE FUNCTIONS ===================== #
def load_database():
    """Loads the Excel database or initializes a new one if missing."""
    if os.path.exists(DB_PATH):
        return pd.read_excel(DB_PATH)
    else:
        st.warning("Database not found! Initializing a new one.")
        empty_df = pd.DataFrame(columns=["Column1", "Column2", "Column3"])
        save_database(empty_df)
        return empty_df

def save_database(data):
    """Saves the updated database."""
    try:
        data.to_excel(DB_PATH, index=False)
        st.success("Database updated successfully!")
    except Exception as e:
        st.error(f"Failed to save database: {e}")

# ===================== FILE PROCESSING FUNCTIONS ===================== #
def extract_text(file, file_type):
    """Extracts text from PDFs or DOCX files."""
    try:
        if file_type == "pdf":
            reader = PdfReader(file)
            return ''.join([page.extract_text() or '' for page in reader.pages])
        elif file_type == "docx":
            doc = Document(file)
            return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"Error reading {file_type.upper()} file: {e}")
        return ""

def upload_data():
    """Handles file uploads and data extraction."""
    uploaded_file = st.file_uploader("Upload a file (CSV, PDF, or DOCX)", type=["csv", "pdf", "docx"])
    if uploaded_file:
        file_type = uploaded_file.type
        try:
            if file_type == "text/csv":
                data = pd.read_csv(uploaded_file)
                st.dataframe(data)
                return data
            elif file_type == "application/pdf":
                text = extract_text(uploaded_file, "pdf")
                st.text_area("PDF Content", text, height=300)
                return text
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = extract_text(uploaded_file, "docx")
                st.text_area("Word Content", text, height=300)
                return text
        except Exception as e:
            st.error(f"Error processing file: {e}")
    return None

# ===================== AI CHATBOT FUNCTION ===================== #
def get_ai_response(user_input):
    """Generates AI response using LLaMA 2 or OpenAI GPT."""
    try:
        if USE_OPENAI:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": user_input}]
            )
            return response["choices"][0]["message"]["content"]
        else:
            response = llm(f"Q: {user_input}\nA: ", max_tokens=150, stop=["Q:", "\n"])
            return response["choices"][0]["text"].strip()
    except Exception as e:
        return f"Error generating response: {e}"

def chatbot():
    """Renders the AI-powered chatbot in the sidebar."""
    st.sidebar.header("Chatbot Assistant")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    for message in st.session_state.chat_history:
        with st.sidebar.chat_message(message["role"]):
            st.markdown(message["content"])
    
    user_input = st.sidebar.chat_input("Ask something...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        response = get_ai_response(user_input)  # AI-generated response
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.sidebar.chat_message("user").markdown(user_input)
        st.sidebar.chat_message("assistant").markdown(response)

# ===================== MAIN APP ===================== #
def main():
    """Main Streamlit app logic."""
    st.title("Med Assist: AI-Powered Diagnostic Assistance and Comfort Chatbot")
    
    st.sidebar.header("Navigation")
    options = st.sidebar.radio("Select a page:", ["Home", "Data Upload", "Database", "About"])
    
    chatbot()  # Add chatbot to sidebar

    if options == "Home":
        st.header("Welcome to Med Assist Dashboard")
        st.write("This app provides AI-powered medical and mental health assistance.")
        st.write("Use the sidebar to navigate.")

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
        st.write("This AI-powered chatbot provides mental health and medical guidance. It offers:")
        st.markdown("""
        - 🧠 **Mental health insights**
        - 🔍 **Symptom analysis**
        - 📊 **Mood tracking**
        - 🎙️ **Voice and text-based conversations**
        - 💡 **Personalized recommendations**
        """)
        st.write("Author: **Adarsh Ojaswi Singh**")

if __name__ == "__main__":
    main()
