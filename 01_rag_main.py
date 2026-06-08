import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# setting the environment

DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(name="growing_vegetables")


user_query = input("What do you want to know about growing vegetables?\n\n")

results = collection.query(
    query_texts=[user_query],
    n_results=4,
    include=["documents", "metadatas", "embeddings", "distances"]
)
print('===========================DOCUMENTS===============================================')
print(results["documents"])

print('===========================METADATA================================================')
print(results["metadatas"])

print('===========================DISTANCES===============================================')
print(results["distances"])

print('===========================EMBEDDINGS==============================================')
print(results["embeddings"])
print('===========================MORE EMBEDDINGS==============================================')

first_embedding = results["embeddings"][0][0]

print(type(first_embedding))
print(len(first_embedding))
print(first_embedding[:10])