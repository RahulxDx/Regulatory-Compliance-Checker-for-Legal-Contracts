import chromadb
from chromadb.config import Settings

# Initialize ChromaDB client
client = chromadb.Client(Settings(
    persist_directory= r"C:\Users\Rahul\Desktop\Regulatory-Compliance-Checker-for-Legal-Contracts/chromadb_storage",
    chroma_db_impl="duckdb+parquet"
))

# Load the collection (assuming the collection is named 'contracts')
collection = client.get_or_create_collection(name="legal_contracts")
def fun(userQuery):
# User query text
    
    
    # Perform similarity search
    results = collection.query(
        query_texts=[userQuery],
        n_results=1  # Retrieve the top match
    )

    print(results["metadatas"])

    category = results["metadatas"][0][0].get('Category', '')
    governing_law = results["metadatas"][0][0].get('Governing Law', '')

    # Print the result
    return f"User Uploaded contract falls under {category} category and follows {governing_law}."