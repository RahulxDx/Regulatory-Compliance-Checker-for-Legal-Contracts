import streamlit as st
import requests
from chromadb import Client
from chromadb.config import Settings
import time
from dotenv import load_dotenv
import os
from groq import Groq

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

def extract_suggestions(text: str) -> str:
    """
    Extracts suggestions from the given text using the Groq API.
    """
    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Give suggestions that should be corrected in the contract"},
            {"role": "user", "content": text},
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
    )
    return completion.choices[0].message.content

def generate_reason_for_similarity(similarity_percentage: float, text: str) -> str:
    """
    Uses Groq LLM to generate a reason for the given similarity percentage.
    """
    prompt = f"The similarity percentage for a contract clause is {similarity_percentage:.2f}%. Explain in detail why this score might have been given based on the contract's text: {text}"
    
    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Analyze the similarity percentage and explain in detail why it was given."},
            {"role": "user", "content": prompt},
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
    )
    return completion.choices[0].message.content

# Initialize ChromaDB client
client = Client(Settings(
    persist_directory=r"C:\\Users\\Rahul\\Desktop\\Regulatory-Compliance-Checker-for-Legal-Contracts\\chromadb_storage",
    chroma_db_impl="duckdb+parquet"
))

# Load the collection
collection = client.get_or_create_collection(name="legal_contracts")

# Streamlit App Configuration
st.set_page_config(page_title="Contract Analyzer", layout="wide")

# Custom Styles
st.markdown(
    """
    <style>
        .stApp { background-color: #f4f4f4; }
        .score-container { display: flex; align-items: center; justify-content: center; }
        .circle {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: bold;
            color: white;
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🔍 Contract Analyzer")
st.sidebar.header("📂 Upload and Analyze Contract")

# Upload file
uploaded_file = st.sidebar.file_uploader("Upload a Contract (.txt, .pdf, .docx):", type=["txt", "pdf", "docx"])

# API Endpoint Configuration
fastapi_url = "http://localhost:8000/extract-text/"

def display_similarity_results(results, text):
    if results:
        st.subheader("📊 Score")
        top_match = results["metadatas"][0][0]
        category = top_match.get("Category", "N/A")
        governing_law = top_match.get("Governing Law", "N/A")
        
        s = results['distances'][0][0]
        similarity_percentage = (1 - (s / 2)) * 100
        color = f"rgb({255 - int(similarity_percentage * 2.55)}, {int(similarity_percentage * 2.55)}, 0)"
        
        # Display results
        st.write(f"**Category:** {category}")
        st.write(f"**Governing Law:** {governing_law}")
        
        # Circular similarity indicator
        st.markdown(
            f"""
            <div class="score-container">
                <div class="circle" style="background-color: {color};">{similarity_percentage:.2f}%</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Generate and display reason for similarity percentage using Groq LLM
        with st.spinner("🔎 Analyzing reason for similarity percentage..."):
            reason = generate_reason_for_similarity(similarity_percentage, text)
        st.subheader("📖 Reason for Similarity Percentage")
        st.write(reason)

# Process the uploaded file
if uploaded_file:
    with st.spinner("🔄 Extracting text and key clauses..."):
        files = {"file": (uploaded_file.name, uploaded_file.read(), uploaded_file.type)}
        response = requests.post(fastapi_url, files=files)

    if response.status_code == 200:
        try:
            response_data = response.json()
            text = response_data.get("extracted_text", "")
            key_clauses = response_data.get("key_clauses", "")
            
            # Display key clauses
            st.subheader("📜 Key Clauses")
            st.markdown(f"{key_clauses}", unsafe_allow_html=True)
            
            # Perform similarity search
            with st.spinner("🔎 Performing similarity search..."):
                similarity_results = collection.query(
                    query_texts=[key_clauses],
                    n_results=1
                )
            display_similarity_results(similarity_results, key_clauses)

            # AI Suggestions Section
            st.subheader("💡 AI Suggestions")
            if key_clauses:
                suggestions = extract_suggestions(key_clauses)  # Get AI suggestions from Groq
                st.write(suggestions)  # Display AI suggestions

        except Exception as e:
            st.error(f"❌ Error processing API response: {str(e)}")
    else:
        st.error(f"❌ Error extracting text: {response.json().get('detail', 'Unknown error')}.")
        
st.sidebar.markdown("--")
