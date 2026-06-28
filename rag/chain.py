import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory as ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from dotenv import load_dotenv

load_dotenv()

# Store session histories in memory
session_histories = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    #Get or create chat history for a session
    if session_id not in session_histories:
        session_histories[session_id] = ChatMessageHistory()
    return session_histories[session_id]


def get_llm():
    
    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3
    )
    return llm


def create_rag_chain(vectorstore):
    """
    How it works:
    1. User asks a question
    2. Retriever fetches relevant chunks from vectorstore
    3. Chunks + question are passed to the LLM
    4. LLM returns an answer based only on the chunks
    5. Chat history is maintained per session
    """

    llm = get_llm()

    # Retriever fetches top 4 similar chunks from vectorstore
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 4}
    )

    # This prompt tells LLM to answer only from the given context
    system_prompt = """You are an HR assistant. Answer questions based only on the HR documents provided below.
If the answer is not in the documents, say "I could not find this information in the HR documents."
Keep your answers clear and simple.

HR Document Context:
{context}"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])

    # Chain that stuffs documents into the prompt
    question_answer_chain = create_stuff_documents_chain(llm, prompt)

    # Full RAG chain = retriever + question answer chain
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    # Wrap with message history so it remembers conversation
    chain_with_history = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer"
    )

    return chain_with_history
