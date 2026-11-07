import streamlit as st
import ollama



st.set_page_config(
    page_title="Nexa Chatbot",
    page_icon="💬",
    layout="centered"
)

st.title("💬 Nexa Chatbot")
st.caption("🚀 Local AI Chatbot powered by Ollama")

# Ollama model
MODEL_NAME = "llama3.2"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! 👋 How can I help you today?"
        }
    ]

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):

    # Display user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.write(prompt)

    # Get response from Ollama
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=st.session_state.messages
        )

        assistant_message = response["message"]["content"]

        # Display assistant response
        with st.chat_message("assistant"):
            st.write(assistant_message)

        # Save assistant response
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_message
            }
        )

    except Exception as error:

        st.error("Unable to connect to Ollama.")

        st.info(
            "Please make sure Ollama is running "
            "and the selected model is installed."
        )

        st.code(str(error))