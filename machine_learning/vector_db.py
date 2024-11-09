import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

def search_same_transactions(df, query: str):
    producst_df = pd.read_csv("Products.csv")

    producst_df["name"] = producst_df["name"].str.strip()

    orders = producst_df.groupby('created_date')['name'].agg(', '.join).reset_index()["name"]

    encoder = SentenceTransformer("all-mpnet-base-v2")
    vectors = encoder.encode(orders)

    vectors = np.array(vectors)

    dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(dimension)

    index.add(vectors)

    k = 10
    search_query = encoder.encode(query).reshape(1, -1)

    distances, indices = index.search(search_query, k)

    return orders.iloc[indices]
