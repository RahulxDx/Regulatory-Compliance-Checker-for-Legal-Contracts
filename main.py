from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from docx import Document
from dotenv import load_dotenv
import os
from groq import Groq  # Assuming Groq client is installed
import uvicorn
import json
from context_rag import fun

s = """
You are a legal document analysis assistant. Your task is to analyze user-uploaded contracts and extract key clauses accurately.

Instructions:
Identify and extract key clauses, including but not limited to:

Parties Involved (Who are the contracting parties?)
Term & Termination (Duration of the contract and termination conditions)
Payment Terms (Pricing, invoicing, late fees, etc.)
Confidentiality (Non-disclosure obligations)
Liability & Indemnification (Who is responsible for damages, indemnity clauses)
Dispute Resolution (Governing law, arbitration, jurisdiction)
Force Majeure (Unexpected events affecting contract execution)
Intellectual Property Rights (Ownership of IP, licensing rights)
Amendment & Assignment (Modification and transferability of the contract)
Other Critical Provisions (Any additional key terms relevant to the contract type)
Output the extracted clauses in a structured format, clearly labeled under appropriate headings.

If a clause is missing or ambiguous, indicate that information is not explicitly stated.

Do not summarize excessively—provide the exact wording where possible.

Your goal is to ensure clarity, accuracy, and completeness in the extraction.
"""
# Load environment variables from .env file
load_dotenv()

# Retrieve API key for Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set in the environment variables or .env file.")

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Text Extractor and Key Clause API! Use the /extract-text/ endpoint to upload files."}

@app.post("/extract-text/")
async def extract_text(file: UploadFile = File(...)):
    """
    Extracts text and key clauses from uploaded files.
    Supported formats: .txt, .pdf, .docx
    """
    try:
        # Check file type and extract text
        if file.filename.endswith(".txt"):
            text = (await file.read()).decode("utf-8")
        elif file.filename.endswith(".pdf"):
            text = extract_text_from_pdf(file)
        elif file.filename.endswith(".docx"):
            text = extract_text_from_docx(file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a .txt, .pdf, or .docx file.")

        # Extract key clauses using Groq
        key_clauses = extract_key_clauses(text)
        
        
        return {"extracted_text": text, "key_clauses": key_clauses}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

def extract_text_from_pdf(file: UploadFile) -> str:
    """
    Extracts text from a PDF file.
    """
    try:
        reader = PdfReader(file.file)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading PDF file: {str(e)}")

def extract_text_from_docx(file: UploadFile) -> str:
    """
    Extracts text from a DOCX file.
    """
    try:
        document = Document(file.file)
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading DOCX file: {str(e)}")

def extract_key_clauses(text: str) -> list:
    """
    Extracts key clauses from the given text using the Groq API.
    """
    try:
        client = Groq(api_key=GROQ_API_KEY)  # Initialize Groq client
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": s},
                {"role": "user", "content": text},
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )
        # Parse response to extract key clauses
        response_text = completion.choices[0].message.content
        
        return response_text

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting key clauses: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
