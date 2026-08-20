import chromadb
from chromadb.utils import embedding_functions

# Use a lightweight default embedding function for ease of local testing
default_ef = embedding_functions.DefaultEmbeddingFunction()

# Initialize ChromaDB client (persistent storage)
client = chromadb.PersistentClient(path="./chroma_db")

# Create or get a collection for trusted facts
try:
    collection = client.get_or_create_collection(
        name="trusted_facts",
        embedding_function=default_ef
    )
except Exception as e:
    print(f"Error initializing ChromaDB: {e}")
    collection = None

# Pre-populate with some mock facts for demonstration
MOCK_FACTS = [
    {
        "id": "fact_1",
        "text": "The moon landing occurred in 1969. NASA successfully landed Apollo 11 on the lunar surface.",
        "source": "NASA Official History"
    },
    {
        "id": "fact_2",
        "text": "The company TechCorp did not file for bankruptcy in 2024. Their recent financial reports show record profits.",
        "source": "Reuters Financial News"
    },
    {
        "id": "fact_3",
        "text": "The new X-99 smartphone does not have a 1-week battery life. Official specifications state it lasts up to 24 hours on a single charge.",
        "source": "Tech Specs Official Database"
    }
]

def initialize_db():
    if not collection:
        return
        
    # Check if we already have facts
    count = collection.count()
    if count == 0:
        print("Populating ChromaDB with mock facts...")
        documents = [fact["text"] for fact in MOCK_FACTS]
        metadatas = [{"source": fact["source"]} for fact in MOCK_FACTS]
        ids = [fact["id"] for fact in MOCK_FACTS]
        
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print("Database populated.")

def retrieve_evidence(query_text: str, n_results: int = 1) -> list:
    """
    Search the vector database for facts relevant to the query.
    """
    if not collection:
        return []
        
    try:
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        evidence_list = []
        if results and results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                doc = results['documents'][0][i]
                meta = results['metadatas'][0][i]
                dist = results['distances'][0][i]
                
                # Only return if the distance is reasonably close (meaning it's relevant)
                # Lower distance = more similar in Chroma (using default L2)
                if dist < 1.5: 
                    evidence_list.append({
                        "text": doc,
                        "source": meta["source"],
                        "relevance_score": round(1.0 - (dist/2.0), 2) # Rough normalization
                    })
        return evidence_list
    except Exception as e:
        print(f"Error querying ChromaDB: {e}")
        return []

# Initialize when the module loads
initialize_db()
