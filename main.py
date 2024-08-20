import streamlit as st
from PyPDF2 import PdfReader
import random
import requests
from datetime import datetime, timedelta
import os
from groq import Groq

# Groq API client setup
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def extract_text_from_pdf(file_path):
    pdf_reader = PdfReader(file_path)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text

def ai_response(question, text, suspect_name, is_criminal):
    prompt = f"Assume you are {'the criminal' if is_criminal else 'a suspect'} named {suspect_name} being investigated by detectives Vector Clark and Shaw Chen in a cyberfraud case involving Maria James. The information about you is: {text[:500]}... The detectives ask: {question}. How do you respond?"

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    if response and response.choices:
        return response.choices[0].message.content.strip()
    else:
        st.error("Error: Could not retrieve response from Groq API.")
        return "Error: Could not retrieve response from Groq API."

def start_timer():
    if "end_time" not in st.session_state:
        st.session_state.end_time = datetime.now() + timedelta(minutes=35)

def check_timer():
    remaining_time = st.session_state.end_time - datetime.now()
    if remaining_time.total_seconds() > 0:
        minutes, seconds = divmod(remaining_time.total_seconds(), 60)
        st.sidebar.write(f"Time remaining: {int(minutes)}:{int(seconds):02d}")
    else:
        st.error("Time's up!")
        st.stop()

# Predefined PDF file paths, suspect names, and images
predefined_files = [
    "file-1.pdf", "file-2.pdf", "file-3.pdf", "file-4.pdf", "file-5.pdf"
]

suspect_names = ["Eve Davis", "Henry Taylor", "Victor Lewis", "Xavier Green", "Helen Coleman"]
suspect_images = ["image-1.png", "image-2.png", "image-3.png", "image-4.png", "image-5.png"]

correct_name = "Victor Lewis"

# Initialize Streamlit session state
st.set_page_config(page_title="AI Investigation Software")
st.title("AI Investigation Software")

start_timer()
check_timer()

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {i: [] for i in range(len(predefined_files))}
if "selected_file_index" not in st.session_state:
    st.session_state.selected_file_index = 0
if "is_criminal" not in st.session_state:
    st.session_state.is_criminal = [suspect == correct_name for suspect in suspect_names]
if "name_guesses" not in st.session_state:
    st.session_state.name_guesses = 0
if "wrong_guesses" not in st.session_state:
    st.session_state.wrong_guesses = 0
if "chat_open" not in st.session_state:
    st.session_state.chat_open = False

# Display images and text input for suspect name guess
cols = st.columns(5)
for i, (suspect_name, suspect_image) in enumerate(zip(suspect_names, suspect_images)):
    with cols[i]:
        if st.button(f"{suspect_name}", key=f"chat_{i}"):
            st.session_state.selected_file_index = i
            st.session_state.chat_open = True
        st.image(suspect_image, use_column_width=True)

user_guess = st.text_input("Enter the suspect's name to solve the case")
if user_guess:
    if user_guess.strip().lower() == correct_name.lower():
        st.success("Correct answer!")
        st.video("https://path_to_success_video.com")
    else:
        st.session_state.wrong_guesses += 1
        if st.session_state.wrong_guesses >= 2:
            st.error("Game over. You've used all your guesses.")
            st.video("https://path_to_failure_video.com")
        else:
            st.error("Incorrect guess. Try again.")

# Chat functionality
if st.session_state.chat_open:
    selected_file_index = st.session_state.selected_file_index
    selected_file_path = predefined_files[selected_file_index]
    suspect_name = suspect_names[selected_file_index]
    text = extract_text_from_pdf(selected_file_path)
    is_criminal = st.session_state.is_criminal[selected_file_index]

    st.header(f"Chat with Suspect {selected_file_index+1}: {suspect_name}")
    st.subheader("PDF Content")
    st.text(text)

    user_question = st.text_input("Ask a question", key=f"input_{selected_file_index}")
    if user_question:
        st.session_state.chat_history[selected_file_index].append(("User", user_question))
        response = ai_response(user_question, text, suspect_name, is_criminal)
        st.session_state.chat_history[selected_file_index].append((suspect_name, response))

    chat_history = st.session_state.chat_history[selected_file_index]
    for speaker, message in chat_history:
        st.write(f"{speaker}: {message}")

# Implementing a confirmation to avoid unintentional page refresh
st.write("""
    <script type="text/javascript">
        window.onbeforeunload = function() {
            return 'Are you sure you want to leave? Your progress will be lost.';
        }
    </script>
""", unsafe_allow_html=True)