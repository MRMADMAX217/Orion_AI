from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import sqlite3
import os 

load_dotenv()

os.environ["LANGCHAIN_PROJECT"] = "Orion"
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

conn = sqlite3.connect(database='chatbot.db2', check_same_thread=False)

# Create metadata table for thread titles
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_metadata (
        thread_id TEXT PRIMARY KEY,
        title TEXT
    )
''')
conn.commit()

# Checkpointer
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    cursor.execute("SELECT thread_id FROM chat_metadata ORDER BY rowid DESC")
    return [row[0] for row in cursor.fetchall()][::-1]




def save_chat_title(thread_id: str, title: str):
    cursor.execute(
        "INSERT OR REPLACE INTO chat_metadata (thread_id, title) VALUES (?, ?)",
        (thread_id, title)
    )
    conn.commit()

def get_chat_title(thread_id: str):
    cursor.execute("SELECT title FROM chat_metadata WHERE thread_id = ?", (thread_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_all_chat_titles():
    cursor.execute("SELECT thread_id, title FROM chat_metadata")
    return dict(cursor.fetchall())

def generate_title_from_message(message: str) -> str:
    """Generate a short descriptive chat title using Gemini."""
    title_prompt = f"Generate a short strictly 3-5 word chat title summarizing this message: '{message}'"
    response = llm.invoke([HumanMessage(content=title_prompt)])
    return response.content.strip()

def delete_chat_thread(thread_id: str):
    """
    Delete a specific chat thread from both LangGraph checkpoints and metadata.
    Works even if certain internal tables don't exist.
    """
    try:
        # 1️⃣ Delete from LangGraph checkpoint table (if it exists)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='checkpoints'")
        if cursor.fetchone():
            cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))

        # 2️⃣ Delete from metadata table
        cursor.execute("DELETE FROM chat_metadata WHERE thread_id = ?", (thread_id,))

        conn.commit()
        print(f"✅ Deleted thread {thread_id} successfully.")

    except sqlite3.Error as e:
        print(f"❌ Error deleting thread {thread_id}: {e}")

def delete_all_threads():
    """
    TEMPORARY: Delete all chat threads from both metadata and LangGraph checkpoints.
    Use with caution — this will remove everything!
    """
    try:
        # 1️⃣ Delete all from LangGraph checkpoints (if table exists)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='checkpoints'")
        if cursor.fetchone():
            cursor.execute("DELETE FROM checkpoints")

        # 2️⃣ Delete all from chat metadata
        cursor.execute("DELETE FROM chat_metadata")

        conn.commit()
        print("✅ All chat threads deleted successfully.")

    except sqlite3.Error as e:
        print(f"❌ Error deleting all threads: {e}")


