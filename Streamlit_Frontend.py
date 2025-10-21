import streamlit as st
from langgraph_database_backend import (
    chatbot,
    retrieve_all_threads,
    get_all_chat_titles,
    save_chat_title,
    generate_title_from_message,
    delete_chat_thread
)
from langchain_core.messages import HumanMessage
import uuid
from dotenv import load_dotenv
import os

# **************************************** UI ENHANCEMENT: Page Configuration *************************************
# This should be the first Streamlit command. It sets the title that appears in the browser tab and the favicon.
st.set_page_config(
    page_title="Orion AI",
    page_icon="🤖"
)

# **************************************** Setup *************************************
load_dotenv()
os.environ["LANGCHAIN_PROJECT"] = "Orion"

# **************************************** Utility Functions *************************
def generate_thread_id():
    return str(uuid.uuid4())

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def get_new_chat_placeholder():
    existing_titles = set(st.session_state['chat_titles'].values())
    i = 1
    while f"New Chat {i}" in existing_titles:
        i += 1
    return f"New Chat {i}"

def reset_chat():
    """Reset chat state for a new conversation."""
    st.session_state['thread_id'] = None
    st.session_state['message_history'] = []
    st.session_state['new_chat_active'] = True

def load_conversation(thread_id):
    """Load conversation history from the backend."""
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])

# **************************************** Session State Initialization **************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = None

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

if 'chat_titles' not in st.session_state:
    st.session_state['chat_titles'] = get_all_chat_titles()

if 'titles_generated' not in st.session_state:
    st.session_state['titles_generated'] = {}

if 'renaming_thread' not in st.session_state:
    st.session_state['renaming_thread'] = None

if 'new_chat_active' not in st.session_state:
    st.session_state['new_chat_active'] = False

if 'active_menu' not in st.session_state:
    st.session_state['active_menu'] = None

# **************************************** Sidebar UI *********************************

# **************************************** Sidebar UI *********************************

with st.sidebar:
    st.title("💬 Orion")

    if st.button("🆕 New Chat", use_container_width=True, key="new_chat_btn"):
        reset_chat()
        st.rerun()

    st.markdown("---")
    st.header("My Conversations")

    chat_threads_to_show = st.session_state['chat_threads'][:]
    if st.session_state.get('new_chat_active', False):
        chat_threads_to_show.append("NEW_CHAT_PLACEHOLDER")

    if chat_threads_to_show:
        for thread_id in reversed(chat_threads_to_show):  # Show newest first
            # VVVV --- FIX IS HERE --- VVVV
            # This check prevents the error by skipping any invalid thread_id entries.
            if thread_id is None:
                continue
            # ^^^^ --- END OF FIX --- ^^^^

            if thread_id == "NEW_CHAT_PLACEHOLDER":
                title = get_new_chat_placeholder()
            else:
                title = st.session_state['chat_titles'].get(thread_id, "Untitled Chat")

            cols = st.columns([8, 1])
            with cols[0]:
                if st.button(title, key=f"chat_{thread_id}", use_container_width=True):
                    if thread_id != "NEW_CHAT_PLACEHOLDER":
                        st.session_state['thread_id'] = thread_id
                        messages = load_conversation(thread_id)
                        st.session_state['message_history'] = [
                            {'role': 'user' if isinstance(msg, HumanMessage) else 'assistant', 'content': msg.content}
                            for msg in messages
                        ]
                        st.session_state['new_chat_active'] = False
                        st.rerun()
                    else:
                        reset_chat()
                        st.rerun()

            with cols[1]:
                if thread_id != "NEW_CHAT_PLACEHOLDER":
                    if st.button("⋮", key=f"menu_{thread_id}", use_container_width=True):
                        st.session_state['active_menu'] = (
                            None if st.session_state.get('active_menu') == thread_id else thread_id
                        )
                        st.rerun()

                # ... (rest of your code remains the same)
            # --- UI for Renaming and Options Menu ---
            if st.session_state.get('renaming_thread') == thread_id:
                new_title = st.text_input(
                    "Rename Chat", value=title, key=f"rename_input_{thread_id}", label_visibility="collapsed"
                )
                r_col1, r_col2 = st.columns(2)
                with r_col1:
                    if st.button("✅ Save", key=f"save_rename_{thread_id}", use_container_width=True):
                        st.session_state['chat_titles'][thread_id] = new_title
                        save_chat_title(thread_id, new_title)
                        st.session_state['renaming_thread'] = None
                        st.rerun()
                with r_col2:
                    if st.button("❌ Cancel", key=f"cancel_rename_{thread_id}", use_container_width=True):
                        st.session_state['renaming_thread'] = None
                        st.rerun()

            if st.session_state.get('active_menu') == thread_id:
                m_col1, m_col2 = st.columns(2)
                with m_col1:
                    if st.button("✏️ Rename", key=f"menu_rename_{thread_id}", use_container_width=True):
                        st.session_state['renaming_thread'] = thread_id
                        st.session_state['active_menu'] = None
                        st.rerun()
                with m_col2:
                    if st.button("🗑️ Delete", key=f"menu_delete_{thread_id}", use_container_width=True):
                        delete_chat_thread(thread_id)
                        st.session_state['chat_threads'].remove(thread_id)
                        st.session_state['chat_titles'].pop(thread_id, None)
                        st.session_state['titles_generated'].pop(thread_id, None)
                        if st.session_state.get('thread_id') == thread_id:
                            reset_chat()
                        st.session_state['active_menu'] = None
                        st.rerun()
    else:
        st.info("No chats yet. Start a new one!")
    st.markdown("---")
    st.caption("🧠 Powered by Dileep + Mohan | Orion’s AI Edition")

# **************************************** Main Chat UI ************************************

# --- UI ENHANCEMENT: Welcome message for new or empty chats ---
# This provides a clean starting point for the user.
if not st.session_state['message_history']:
    st.markdown(
        """
        <div style="text-align: center; padding: 4rem 1rem;">
            <h1 style="font-size: 3rem;">🤖 Orion AI</h1>
            <p style="font-size: 1.2rem; color: #888;">Your intelligent assistant. Start a conversation by typing below!</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Display existing messages from history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# Chat input widget with a static key
user_input = st.chat_input("Type here...", key="chat_input")

if user_input:
    # Set a flag to check if we need to rerun for a title update later
    rerun_for_title_update = False

    # Create a new thread if this is the first message of a new chat
    if st.session_state.get('new_chat_active', False):
        thread_id = generate_thread_id()
        st.session_state['thread_id'] = thread_id
        add_thread(thread_id)
        placeholder_title = get_new_chat_placeholder()
        st.session_state['chat_titles'][thread_id] = placeholder_title
        save_chat_title(thread_id, placeholder_title)
        st.session_state['new_chat_active'] = False

    # Display user's message and add to history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.markdown(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}
    current_thread_id = st.session_state['thread_id']

    # --- Auto-generate and store chat title ---
    TRIVIAL_MESSAGES = {"hi","hii", "hello", "hey", "bye", "goodbye", "ok", "thanks", "thank you"}
    message_text = user_input.strip().lower()

    if not st.session_state['titles_generated'].get(current_thread_id, False):
        if message_text not in TRIVIAL_MESSAGES:
            with st.spinner("Generating title..."):
                title = generate_title_from_message(user_input)
                st.session_state['chat_titles'][current_thread_id] = title
                save_chat_title(current_thread_id, title)
                st.session_state['titles_generated'][current_thread_id] = True
                rerun_for_title_update = True # Set flag to update sidebar

    # --- Stream assistant response ---
    with st.chat_message('assistant'):
        stream = chatbot.stream(
            {'messages': [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode='messages'
        )
        full_response = st.write_stream(
            (message_chunk.content for message_chunk, metadata in stream)
        )

    # Append the complete assistant message to history for future display
    st.session_state['message_history'].append({'role': 'assistant', 'content': full_response})

    # Rerun to update the sidebar with the new title if it was just generated
    if rerun_for_title_update:
        st.rerun()
