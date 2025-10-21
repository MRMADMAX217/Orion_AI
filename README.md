# 🤖 Orion AI Chatbot

A multi-conversation chatbot application built with Streamlit, LangGraph, and Google Gemini. This project demonstrates how to create a persistent, stateful chat experience where users can manage multiple conversations, which are saved to a SQLite database.



This application provides a clean user interface for interacting with an AI, with all conversation history neatly organized and accessible in a sidebar.

---

## ✨ Key Features

* **Multi-Conversation Management:** Users can create, switch between, rename, and delete multiple chat threads seamlessly.
* **Persistent Memory:** Chat history is saved using LangGraph's `SqliteSaver`, allowing conversations to be resumed across sessions. The chat titles are stored in a separate SQLite table for quick retrieval.
* **Streaming Responses:** The assistant's messages are streamed in real-time, providing a dynamic and engaging user experience.
* **Automatic Title Generation:** New chats are automatically given a short, descriptive title based on the content of the first user message.
* **Intuitive UI:** A clean and modern user interface built with Streamlit, featuring a sidebar for easy navigation of past conversations.
* **Powered by Gemini:** Leverages Google's powerful `gemini-2.5-flash` model via the LangChain library for intelligent and coherent responses.

---

## 🛠️ Technology Stack

* **Frontend:** [Streamlit](https://streamlit.io/)
* **Backend Logic:** [LangGraph](https://python.langchain.com/docs/langgraph/)
* **LLM:** [Google Gemini](https://ai.google.dev/)
* **Database:** [SQLite](https://www.sqlite.org/index.html)
* **Core Libraries:** [LangChain](https://www.langchain.com/), `python-dotenv`

---

## 🚀 Getting Started

Follow these instructions to set up and run the project on your local machine.

### 1. Prerequisites

* Python 3.8+
* A **Google API Key**. You can obtain one from [Google AI Studio](https://makersuite.google.com/app/apikey).

### 2. Clone the Repository

```bash
git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
cd your-repository-name
```

### 3. Set Up a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
# For Mac/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

### 4. Install Dependencies

Create a file named `requirements.txt` in the root of your project directory and add the following lines:

```text
streamlit
langgraph
langchain
langchain-core
langchain-google-genai
python-dotenv
```

Now, install these packages using pip:

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a file named `.env` in the root of your project directory. This file will store your secret API key. Add your Google API key to it like this:

```text
GOOGLE_API_KEY="your_google_api_key_here"
```

### 6. Run the Application

Once the setup is complete, you can run the Streamlit application with the following command:

```bash
streamlit run frontend.py
```

Open your web browser and navigate to the local URL provided by Streamlit (usually `http://localhost:8501`). A database file named `chatbot.db2` will be automatically created in your project directory on the first run.

---

## 📁 File Structure

The project is organized into two main files:

* `frontend.py`: Contains all the Streamlit code for the user interface, session state management, and interaction logic.
* `langgraph_database_backend.py`: Sets up the LangGraph agent, configures the SQLite database and checkpointer for persistence, and provides all the helper functions for interacting with the database.

---

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
