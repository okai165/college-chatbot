from app.rag.retriever import retrieve_similar_chunks

results = retrieve_similar_chunks("What is cloud computing?")

for row in results:
    print("\n")
    print(row.content)
    print("Distance:", row.distance)