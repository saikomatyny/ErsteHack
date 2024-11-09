import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from . import model


class VectorDB:

    def __init__(self):
        self.index = None

    def create_vectordb(self):
        products_df = pd.read_csv("Products.csv")

        products_df["name"] = products_df["name"].str.strip()

        orders = products_df.groupby('created_date')['name'].agg(', '.join).reset_index()["name"]

        encoder = SentenceTransformer("all-mpnet-base-v2")
        vectors = encoder.encode(orders)

        vectors = np.array(vectors)

        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)

        dimension = vectors.shape[1]

        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(vectors)
    
    def load_vectordb(self, path):
        with open("index.pkl", "rb") as file:
            self.index = pickle.load(file)


    def search_same_transactions(self, df, query: str):

        df["name"] = df["name"].str.strip()
        orders = df.groupby('created_date')['name'].agg(', '.join).reset_index()["name"]

        encoder = SentenceTransformer("all-mpnet-base-v2")
        vectors = encoder.encode(orders)
        vectors = np.array(vectors)


        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)

        dimension = vectors.shape[1]

        index = faiss.IndexFlatL2(dimension)
        index.add(vectors)

        search_query = encoder.encode(query).reshape(1, -1)

        distances, indices = index.search(search_query, k=1)

        indices = indices.flatten()  
        result_orders = orders.iloc[indices]

        return result_orders.tolist()[0]

