import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# Step 1: Load the dataset
df = pd.read_csv(r"C:\Users\Rahul\Desktop\Regulatory-Compliance-Checker-for-Legal-Contracts\updated_dataset.csv")

# Step 2: Drop unnecessary columns
columns_to_drop = ["Document Name", "Notice to terminate renewal", "Notice to Terminate Renewal",
                   "Post-Termination Services", "Discrepancy", "Filename"]
df = df.drop(columns=[col for col in columns_to_drop if col in df.columns], axis=1)
df = df[df['contract'].notna() & df['contract'].str.strip().ne('')]


# Step 3: Initialize the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight and efficient model

# Step 4: Generate embeddings for the 'contract' column
df['embedding'] = df['contract'].apply(lambda x: model.encode(str(x)))

# Step 5: Initialize ChromaDB client
client = chromadb.Client(Settings(
    persist_directory=r"C:\Users\Rahul\Desktop\Regulatory-Compliance-Checker-for-Legal-Contracts/chromadb_storage",  # Directory for persistent storage
    chroma_db_impl="duckdb+parquet"         # Use DuckDB with Parquet for storage
))

# Step 6: Create a collection in ChromaDB
collection = client.get_or_create_collection(name="legal_contracts")

# Step 7: Add data to ChromaDB
for index, row in df.iterrows():
    collection.add(
        documents=[row['contract']],  # The contract text
        metadatas={"Category": row['Category'], "Governing Law": row['Governing Law']},  # Metadata
        ids=[f"doc_{index}"]  # Unique ID for each document
    )

print("Embeddings and metadata successfully stored in ChromaDB!")
