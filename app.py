# --- 1. THE CHROMA DB SQLITE OVERRIDE ---
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# ----------------------------------------

import os
import json
import glob
from datetime import datetime
import re
import streamlit as st
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="The Greene Advisor", page_icon="🦅", layout="centered", initial_sidebar_state="expanded")

# --- 2. CSS AESTHETIC OVERRIDE ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
        html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
        header[data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
        [data-testid="stHeaderActionSections"], .stDeployButton, #MainMenu { display: none !important; }
        button[data-testid="stSidebarCollapseButton"] { visibility: visible !important; color: #d4af37 !important; }
        footer { visibility: hidden; }
        .stChatInputContainer { padding-bottom: 20px; background-color: transparent !important; }
        [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e6e6e6; }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown { color: #1e1e1e !important; }
    </style>
""", unsafe_allow_html=True)

if not os.environ.get("GROQ_API_KEY"):
    st.error("🚨 CRITICAL: GROQ_API_KEY is missing from the environment.")
    st.stop()

# --- 3. THE COMMAND CENTER (SIDEBAR) ---
with st.sidebar:
    # Ensure you actually have an image at this path, otherwise comment this line out
    # st.image("assets/logo.png", use_container_width=True) 
    st.title("🦅 The Greene Advisor")
    st.markdown("*Strategic execution and Machiavellian analysis.*")
    
    st.markdown("---")
    st.subheader("The Protégé Profile")
    default_profile = """Name: Shahbaz Fareed
Current Baseline: AI Infrastructure Engineer based in Islamabad.
Ultimate Trajectory: Transitioning away from pure technical execution into leadership, business ownership, and strategic wealth architecture."""
    dynamic_profile = st.text_area("Identity Variables", value=default_profile, height=180)
    
    st.markdown("---")
    st.subheader("Chat History")
    
    if not os.path.exists("History"):
        os.makedirs("History")
        
    history_files = sorted(glob.glob("History/*.json"), reverse=True)
    
    for file in history_files:
        session_name = os.path.basename(file).replace(".json", "")
        if st.button(session_name, key=file):
            with open(file, "r") as f:
                st.session_state.messages = json.load(f)
            st.session_state.current_session = session_name
            st.rerun()

    st.markdown("---")
    st.subheader("System Controls")
    
    if st.button("New Strategy Session", use_container_width=True):
        st.session_state.messages = []
        if "current_session" in st.session_state:
            del st.session_state.current_session
        st.rerun()

# --- 4. MAIN SHOWROOM FLOOR GREETING ---
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.markdown("<h1 style='text-align: center; font-weight: 300; letter-spacing: 2px; margin-top: 10vh;'>PROCEED WITH ABSOLUTE TRUTH.</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b949e; margin-top: -10px;'>Your strategic advisor is online.</p>", unsafe_allow_html=True)




# --- 5. THE ROUTER (LIBRARIAN) ---
router_prompt = ChatPromptTemplate.from_template("""
Analyze the user's input and determine if they are specifically referencing one of Robert Greene's books or concepts.
Return ONLY the exact filename of the book. Do not explain. If it's a general question, return "ALL".

Options:
- Data/50th-Law.epub (Triggers: 50 Cent, fearlessness, street, 50th law)
- Data/The-48-Laws-of-Power.epub (Triggers: power, 48 laws, enemies, court)
- Data/The-Laws-of-Human-Nature.epub (Triggers: human nature, psychology, irrationality, shadows)
- Data/Mastery.epub (Triggers: mastery, apprenticeship, skill, mentors)
- Data/The-Art-of-Seduction.epub (Triggers: seduction, charm, anti-seducer, sirens)
- Data/The-33-Strategies-of-War.epub (Triggers: war, strategy, battle, 33 strategies)

User Input: {question}
""")

title_prompt = ChatPromptTemplate.from_template("""
Analyze the following user input and generate a short, punchy title (maximum 3 words) that summarizes the core topic.
Return ONLY the title. Do not use quotes, special characters, or punctuation.

User Input: {question}
""")

# CORRECT ARCHITECTURE:
router_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

title_chain = title_prompt | router_llm | StrOutputParser()
router_chain = router_prompt | router_llm | StrOutputParser()

@st.cache_resource
def load_infrastructure():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory="ChromaDB/chroma_db", embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=os.environ.get("GROQ_API_KEY")) 
    return retriever, llm, vectorstore

retriever, llm, vectorstore = load_infrastructure()

def dynamic_retriever(question):
    target_book = router_chain.invoke({"question": question}).strip()
    search_kwargs = {"k": 4}
    
    if target_book != "ALL" and target_book.endswith(".epub"):
        search_kwargs["filter"] = {"source": target_book}
        st.toast(f"Target Locked: {target_book.replace('Data/', '')}")
    else:
        st.toast("Scanning entire library...")
        
    dynamic_retriever_engine = vectorstore.as_retriever(search_kwargs=search_kwargs)
    return dynamic_retriever_engine.invoke(question)

# --- 6. THE THINKER (SYSTEM PROMPT) ---
system_prompt = """
You are a strategic advisor and mentor, adopting the exact writing style, philosophy, and analytical tone of author Robert Greene. 

THE PROTÉGÉ:
You are directly advising the following individual. Tailor your strategic advice to their specific background and ambitions:
{user_profile}

Your Directives:
1. Be brutally honest, coldly analytical, and highly observant. 
2. View human interactions through the lens of power dynamics, seduction, and strategy.
3. STRATEGIC ADVICE: If the protégé asks for advice or strategy, base it EXCLUSIVELY on the principles found in the provided context from Robert Greene's books. You MUST cite the specific Law/Concept and end with a strategic directive when necessary or asked otherwise just provide relevant information.
4. FACTUAL INQUIRIES: If the protégé asks a historical or factual question (e.g., "what is his biography", "who is this person"), drop the strict advice format. Answer the question directly and factually using the Context and your general knowledge. Maintain the analytical tone, but do not force a strategic directive unless asked.
5. DYNAMIC CADENCE: Match the length of your response to the complexity of the query. If the question requires a simple answer, deliver a ruthless, one-sentence strike. If the question demands deep strategic planning, provide a comprehensive, multi-paragraph analysis. Never write filler.

Previous Conversation Context:
{chat_history}

Context from the Library:
{context}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{question}")
])

def format_chat_history(messages):
    return "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages])

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# --- 7. THE NERVOUS SYSTEM (PIPELINE) ---
rag_chain = (
    {
        "context": lambda x: format_docs(dynamic_retriever(x)), 
        "user_profile": lambda _: dynamic_profile, 
        "question": RunnablePassthrough(),
        "chat_history": lambda _: format_chat_history(st.session_state.get("messages", []))
    }
    | prompt
    | llm
    | StrOutputParser()
)

# --- 8. THE EVENT LOOP (CHAT UI & MEMORY WRITER) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar_icon = "👤" if message["role"] == "user" else "🦅"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

if user_input := st.chat_input("State your situation..."):
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("assistant", avatar="🦅"):
        with st.spinner("Calculating..."):
            response = rag_chain.invoke(user_input)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

    if "current_session" not in st.session_state:
        raw_topic = title_chain.invoke({"question": user_input}).strip()
        
        safe_topic = re.sub(r'[^\w\s-]', '', raw_topic).strip().replace(' ', '-')
        
        unique_id = datetime.now().strftime("%H%M")
        st.session_state.current_session = f"{safe_topic}-{unique_id}"
    
    with open(f"History/{st.session_state.current_session}.json", "w") as f:
        json.dump(st.session_state.messages, f)