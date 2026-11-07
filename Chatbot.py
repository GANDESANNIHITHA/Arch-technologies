import streamlit as st
import ollama
import json
import os
import uuid


# ============================================================
# FILE SETTINGS
# ============================================================

HISTORY_FILE = "chat_history.json"


# ============================================================
# LOAD CHAT HISTORY
# ============================================================

def load_chat_history():

    if not os.path.exists(HISTORY_FILE):
        return {}

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            history = json.load(file)

        # Add properties to older chats
        for chat_id, chat_data in history.items():

            chat_data.setdefault(
                "pinned",
                False
            )

            chat_data.setdefault(
                "archived",
                False
            )

        return history

    except Exception:

        return {}


# ============================================================
# SAVE CHAT HISTORY
# ============================================================

def save_chat_history(history):

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            history,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# SAVE CURRENT CHAT
# ============================================================

def save_current_chat():

    # Don't save only the initial greeting
    if len(
        st.session_state.messages
    ) <= 1:

        return

    # Find first user message
    first_user_message = next(

        (
            message["content"]

            for message
            in st.session_state.messages

            if message["role"] == "user"
        ),

        "New Chat"
    )

    # Get old chat settings
    old_chat = st.session_state.chat_history.get(
        st.session_state.chat_id,
        {}
    )

    # Save conversation
    st.session_state.chat_history[
        st.session_state.chat_id
    ] = {

        "title": old_chat.get(
            "title",
            first_user_message[:40]
        ),

        "messages": st.session_state.messages,

        "pinned": old_chat.get(
            "pinned",
            False
        ),

        "archived": old_chat.get(
            "archived",
            False
        )
    }

    save_chat_history(
        st.session_state.chat_history
    )


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(

    page_title="Nexa Chatbot",

    page_icon="💬",

    layout="centered"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

/* =========================================
   CHAT INPUT CONTAINER
   ========================================= */

div[data-testid="stChatInput"] {
    position: relative !important;
}


/* =========================================
   PLUS BUTTON
   ========================================= */

.plus-container {
    position: fixed !important;

    bottom: 22px !important;

    z-index: 999999 !important;

    width: 42px !important;

    height: 42px !important;

    display: flex !important;

    align-items: center !important;

    justify-content: center !important;

    pointer-events: auto !important;
}


/* =========================================
   PLUS BUTTON ITSELF
   ========================================= */

.plus-container button {
    width: 38px !important;

    height: 38px !important;

    min-height: 38px !important;

    padding: 0 !important;

    margin: 0 !important;

    border: none !important;

    background: transparent !important;

    box-shadow: none !important;

    border-radius: 50% !important;

    font-size: 25px !important;

    color: #222 !important;

    display: flex !important;

    align-items: center !important;

    justify-content: center !important;
}


.plus-container button:hover {
    background: rgba(0,0,0,0.06) !important;
}


/* =========================================
   CHAT INPUT TEXT
   ========================================= */

div[data-testid="stChatInput"] textarea {
    padding-left: 45px !important;
}


/* =========================================
   CHAT INPUT
   ========================================= */

div[data-testid="stChatInput"] {
    border-radius: 28px !important;

    border: 1px solid #d9d9d9 !important;

    background: white !important;

    box-shadow:
        0 1px 4px rgba(0,0,0,0.08) !important;
}


/* =========================================
   CHAT HISTORY BUTTON
   ========================================= */

.history-button button {

    border: none !important;

    background: transparent !important;

    box-shadow: none !important;

    padding: 6px 4px !important;

    text-align: left !important;

    width: 100% !important;
}


.history-button button:hover {

    background-color:
        rgba(128,128,128,0.12) !important;
}


/* =========================================
   PIN BUTTON
   ========================================= */

.pin-button button {

    border: none !important;

    background: transparent !important;

    box-shadow: none !important;

    padding: 4px !important;

    min-width: 30px !important;
}


/* =========================================
   THREE DOT BUTTON
   ========================================= */

.menu-button button {

    border: none !important;

    background: transparent !important;

    box-shadow: none !important;

    padding: 4px !important;

    min-width: 30px !important;
}


/* =========================================
   MOBILE
   ========================================= */

@media (max-width: 768px) {

    .plus-container {

        left: 20px !important;

    }

}

</style>
""", unsafe_allow_html=True)


# ============================================================
# INITIALIZE CHAT HISTORY
# ============================================================

if "chat_history" not in st.session_state:

    st.session_state.chat_history = (
        load_chat_history()
    )


# ============================================================
# CREATE CHAT ID
# ============================================================

if "chat_id" not in st.session_state:

    st.session_state.chat_id = str(
        uuid.uuid4()
    )


# ============================================================
# INITIALIZE CURRENT CONVERSATION
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = [

        {
            "role": "assistant",

            "content":
                "Hello! 👋 How can I help you today?"
        }

    ]


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # ========================================================
    # NEW CHAT
    # ========================================================

    st.divider()

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        # Save current chat
        save_current_chat()

        # Create new chat ID
        st.session_state.chat_id = str(
            uuid.uuid4()
        )

        # Reset messages
        st.session_state.messages = [

            {
                "role": "assistant",

                "content":
                    "Hello! 👋 How can I help you today?"
            }

        ]

        st.rerun()


    # ========================================================
    # CHAT HISTORY
    # ========================================================

    st.divider()

    st.subheader(
        "🕘 Chat History"
    )


    # ========================================================
    # GET ACTIVE CHATS
    # ========================================================

    active_chats = {

        chat_id: chat_data

        for chat_id, chat_data
        in st.session_state.chat_history.items()

        if not chat_data.get(
            "archived",
            False
        )
    }


    # ========================================================
    # PINNED CHATS FIRST
    # ========================================================

    sorted_chats = sorted(

        active_chats.items(),

        key=lambda item:
            not item[1].get(
                "pinned",
                False
            )
    )


    # ========================================================
    # DISPLAY CHAT HISTORY
    # ========================================================

    if sorted_chats:

        for chat_id, chat_data in sorted_chats:

            title = chat_data.get(
                "title",
                "Previous Chat"
            )

            is_pinned = chat_data.get(
                "pinned",
                False
            )


            # =================================================
            # CHAT ROW
            # =================================================

            row = st.container(
                key=f"row_{chat_id}"
            )


            with row:

                title_col, pin_col, menu_col = (
                    st.columns(
                        [7, 1, 1],
                        gap="small"
                    )
                )


                # =============================================
                # CHAT TITLE
                # =============================================

                with title_col:

                    st.markdown(
                        '<div class="history-button">',
                        unsafe_allow_html=True
                    )


                    if st.button(

                        f"💬 {title}",

                        key=f"history_{chat_id}",

                        use_container_width=True,

                        help="Open conversation"
                    ):

                        st.session_state.chat_id = (
                            chat_id
                        )

                        st.session_state.messages = (
                            chat_data["messages"]
                        )

                        st.rerun()


                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True
                    )


                # =============================================
                # PIN
                # =============================================

                with pin_col:

                    st.markdown(
                        '<div class="pin-button">',
                        unsafe_allow_html=True
                    )


                    if is_pinned:

                        pin_icon = "📌"

                        pin_help = "Unpin chat"

                    else:

                        pin_icon = "📍"

                        pin_help = "Pin chat"


                    if st.button(

                        pin_icon,

                        key=f"pin_{chat_id}",

                        help=pin_help
                    ):

                        st.session_state.chat_history[
                            chat_id
                        ]["pinned"] = (
                            not is_pinned
                        )

                        save_chat_history(
                            st.session_state.chat_history
                        )

                        st.rerun()


                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True
                    )


                # =============================================
                # THREE DOTS
                # =============================================

                with menu_col:

                    st.markdown(
                        '<div class="menu-button">',
                        unsafe_allow_html=True
                    )


                    with st.popover(
                        "⋯",
                        help="Chat options"
                    ):

                        st.markdown(
                            "### Chat Options"
                        )


                        # =================================
                        # RENAME
                        # =================================

                        st.markdown(
                            "#### ✏️ Rename"
                        )


                        new_title = st.text_input(

                            "Chat name",

                            value=title,

                            key=(
                                f"rename_input_{chat_id}"
                            ),

                            label_visibility="collapsed"
                        )


                        if st.button(

                            "Save Name",

                            key=(
                                f"rename_{chat_id}"
                            ),

                            use_container_width=True
                        ):

                            new_title = (
                                new_title.strip()
                            )


                            if new_title:

                                st.session_state.chat_history[
                                    chat_id
                                ]["title"] = (
                                    new_title
                                )

                                save_chat_history(
                                    st.session_state.chat_history
                                )

                                st.rerun()


                        st.divider()


                        # =================================
                        # SHARE
                        # =================================

                        st.markdown(
                            "#### 📤 Share"
                        )


                        share_text = ""


                        for message in chat_data.get(

                            "messages",

                            []
                        ):

                            role = (
                                message["role"]
                                .capitalize()
                            )

                            content = (
                                message["content"]
                            )

                            share_text += (

                                f"{role}:\n"

                                f"{content}\n\n"
                            )


                        st.download_button(

                            label="📤 Download Chat",

                            data=share_text,

                            file_name=(
                                f"{title[:30]}.txt"
                            ),

                            mime="text/plain",

                            key=(
                                f"share_{chat_id}"
                            ),

                            use_container_width=True
                        )


                        st.divider()


                        # =================================
                        # ARCHIVE
                        # =================================

                        if st.button(

                            "📦 Archive",

                            key=(
                                f"archive_{chat_id}"
                            ),

                            use_container_width=True
                        ):

                            st.session_state.chat_history[
                                chat_id
                            ]["archived"] = True

                            save_chat_history(
                                st.session_state.chat_history
                            )

                            st.rerun()


                        # =================================
                        # DELETE
                        # =================================

                        if st.button(

                            "🗑️ Delete",

                            key=(
                                f"delete_{chat_id}"
                            ),

                            use_container_width=True
                        ):

                            del st.session_state.chat_history[
                                chat_id
                            ]

                            save_chat_history(
                                st.session_state.chat_history
                            )

                            st.rerun()


                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True
                    )


    else:

        st.caption(
            "No previous chats yet."
        )


# ============================================================
# MAIN CHAT
# ============================================================

st.title(
    "💬 Nexa Chatbot"
)

st.caption(
    "🚀 Local AI Chatbot powered by Ollama"
)


# ============================================================
# OLLAMA MODEL
# ============================================================

MODEL_NAME = "llama3.2"


# ============================================================
# DISPLAY PREVIOUS MESSAGES
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.write(
            message["content"]
        )


# ============================================================
# PLUS MENU
# ============================================================

st.markdown(
    '<div class="plus-container">',
    unsafe_allow_html=True
)


with st.popover(
    "＋",
    help="Add files, images and more"
):

    st.markdown(
        "### Add to your chat"
    )


    # ========================================================
    # FILES
    # ========================================================

    st.markdown(
        "#### 📎 Files"
    )


    uploaded_file = st.file_uploader(

        "Upload a file",

        type=[
            "txt",
            "md",
            "pdf",
            "docx",
            "csv"
        ],

        key="chat_file_upload",

        label_visibility="collapsed"
    )


    if uploaded_file is not None:

        st.success(
            f"📎 {uploaded_file.name} added"
        )


    st.divider()


    # ========================================================
    # IMAGES
    # ========================================================

    st.markdown(
        "#### 🖼️ Images"
    )


    uploaded_image = st.file_uploader(

        "Upload an image",

        type=[
            "png",
            "jpg",
            "jpeg",
            "webp"
        ],

        key="chat_image_upload",

        label_visibility="collapsed"
    )


    if uploaded_image is not None:

        st.image(

            uploaded_image,

            caption=uploaded_image.name,

            width=250
        )

        st.success(
            "🖼️ Image added"
        )


    st.divider()


    # ========================================================
    # GENERATE IMAGES
    # ========================================================

    st.markdown(
        "#### 🎨 Generate Images"
    )


    if st.button(

        "🎨 Generate an image",

        use_container_width=True
    ):

        st.info(
            "Image generation selected."
        )


    st.divider()


    # ========================================================
    # LIBRARIES
    # ========================================================

    st.markdown(
        "#### 📚 Add Libraries"
    )


    if st.button(

        "📚 Browse Libraries",

        use_container_width=True
    ):

        st.info(
            "Library selection selected."
        )


st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# CHAT INPUT
# ============================================================

if prompt := st.chat_input(
    "Ask anything"
):

    # ========================================================
    # ADD USER MESSAGE
    # ========================================================

    st.session_state.messages.append(

        {
            "role": "user",

            "content": prompt
        }
    )


    # ========================================================
    # DISPLAY USER MESSAGE
    # ========================================================

    with st.chat_message(
        "user"
    ):

        st.write(
            prompt
        )


    # ========================================================
    # GET RESPONSE FROM OLLAMA
    # ========================================================

    try:

        response = ollama.chat(

            model=MODEL_NAME,

            messages=(
                st.session_state.messages
            )
        )


        assistant_message = (
            response[
                "message"
            ][
                "content"
            ]
        )


        # ====================================================
        # DISPLAY ASSISTANT RESPONSE
        # ====================================================

        with st.chat_message(
            "assistant"
        ):

            st.write(
                assistant_message
            )


        # ====================================================
        # SAVE ASSISTANT RESPONSE
        # ====================================================

        st.session_state.messages.append(

            {
                "role": "assistant",

                "content": assistant_message
            }
        )


        # ====================================================
        # SAVE CURRENT CHAT
        # ====================================================

        save_current_chat()


    except Exception as error:

        st.error(
            "Unable to connect to Ollama."
        )

        st.info(

            "Please make sure Ollama is running "
            "and the selected model is installed."
        )

        st.code(
            str(error)
        )