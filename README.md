Med Assist: AI-Powered Diagnostic Assistance and Comfort Chatbot

Overview

Med Assist is an AI-driven chatbot designed to assist users in diagnosing common health issues based on symptoms and providing general medical guidance. The chatbot leverages natural language processing (NLP) and a structured dataset to provide accurate and relevant responses.

Features

Symptom-Based Diagnosis: Users can describe their symptoms, and the chatbot provides possible medical conditions and recommendations.

Prescription Upload & Analysis: Users can upload previous prescriptions (PDF, DOCX), and the system extracts relevant data.

Interactive Chatbot: Engages users with an intelligent, human-like conversation.

Personalized Recommendations: Provides treatment suggestions, home remedies, and lifestyle modifications.

Secure & User-Friendly Interface: Ensures data privacy and an intuitive experience.

System Architecture

The system consists of the following components:

User Interface: Built with Streamlit, enabling interactive conversations and file uploads.

Database: Stores medical questions, responses, and past interactions for better learning.

NLP Engine: Uses fuzzy matching to find the most relevant response from the dataset.

Data Processing Modules: Extracts text from uploaded prescriptions (PDF, DOCX) and incorporates the data into the chatbot.

AI Model: Processes inputs, identifies symptoms, and provides suitable responses.

Technology Stack

Programming Language: Python

Libraries & Frameworks: Streamlit, Pandas, FuzzyWuzzy, PyPDF2, Python-docx

Database: XLSX-based structured dataset

Machine Learning & NLP: Text processing for understanding user queries

Installation & Setup

Prerequisites:

Ensure you have Python 3.8+ installed.

Steps to Run the Project:

Clone the repository:

git clone https://github.com/your-repo/med-assist-chatbot.git
cd med-assist-chatbot

Install dependencies:

pip install -r requirements.txt

Run the application:

streamlit run src/streamlit_app.py

Upload a dataset (indian_health_chatbot_dataset.xlsx) if required.

Dataset

The chatbot operates using a structured dataset containing:

Medical Questions: Common user queries about symptoms.

Responses: AI-generated and expert-approved answers.

Symptoms & Conditions: Data for diagnosing common illnesses.

Usage

Launch the app and start a conversation with the chatbot.

Upload past prescriptions for personalized suggestions.

Ask about symptoms, and the chatbot will provide relevant medical insights.

Future Enhancements

Voice-based interaction support

Integration with real-time medical databases

Advanced AI-driven diagnosis models

Mobile application development

Contributing

Contributions are welcome! Fork the repository and submit pull requests for improvements.

License

This project is licensed under the MIT License. See LICENSE for details.
