import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from . import vector_database

class Model:
    def frequent_users(self):
        products_df = pd.read_csv("Products.csv")

        data = products_df["created_by"].value_counts().to_dict()
        products_number = pd.DataFrame.from_dict(data, orient='index', columns=['Value']).reset_index()
        products_number.columns = ['created_by', 'count_products']
        receipts_number =  products_df.groupby(by=["created_date", "created_by"]).size().reset_index(name='count').groupby(by="created_by").aggregate("count").reset_index()[["created_by", "count"]]
        frequency_df = pd.merge(products_number, receipts_number, on="created_by")

        frequency_df["frequency"] = frequency_df["count_products"]/frequency_df["count"]
        frequency_df["log_frequency"] = np.log(frequency_df["frequency"])
        frequency_df["is_frequent"] = frequency_df["log_frequency"] > 2*frequency_df["log_frequency"].std()

        return frequency_df[["created_by", "is_frequent"]]


    def discount_users(self):
        products_df = pd.read_csv("Products.csv")
        orders = products_df.groupby('created_date')['name'].agg(', '.join).reset_index()
        orders["name"] =  orders["name"].str.lower()
        orders["has_discount"] = orders["name"].str.contains("|".join(["zľava", "kaufland card"]), case=False)

        return orders[["created_date", "has_discount"]]


    def extend_dataframe(self, products_df):

        organizations = pd.read_csv("Organizations.csv")
        organizations.rename(columns={"id": "organization_id"}, inplace=True)

        
        df_temp = pd.merge(products_df, self.frequent_users(), on="created_by", how="inner")
        df_temp = pd.merge(df_temp, self.discount_users(), on="created_date", how="inner")
        df_temp = pd.merge(df_temp, organizations[["organization_id", "municipality"]], on="organization_id", how="inner")

        df_temp["name"] = df_temp["name"].str.strip()

        return df_temp

    def user_info(self, user_id):
        products_df = self.extend_dataframe(pd.read_csv("Products.csv"))
        return products_df[products_df["created_by"] == user_id].iloc[-1][["has_discount", "is_frequent", "municipality", "category"]].tolist()


    def filtered_dataframe(self, products_df, user_id):
        requirements = self.user_info(user_id)
        return products_df[(products_df["has_discount"] == requirements[0]) & (products_df["is_frequent"] == requirements[1]) & (products_df["municipality"] == requirements[2]) & (products_df["category"] == requirements[3])]


    def get_answer(self, query, user_id):
        products_df = pd.read_csv("Products.csv")

        vector_db = vector_database.VectorDB()
        vector_db.load_vectordb(".")
        result = vector_db.search_same_transactions(self.filtered_dataframe(self.extend_dataframe(products_df), user_id), query)
        
        result = result.split(",")
        query = query.split(",")
        result = [i for i in result if i not in query]

        if result != []:
            return result
        else:
            return result


    def get_full_answer(self, query, user_id):
        result = self.get_answer(query, user_id)
        final_result = []

        products_df = pd.read_csv("Products.csv")
        df = self.filtered_dataframe(self.extend_dataframe(products_df), 7)

        for product in result:    
            temp_df = df[df["name"] == product]
            final_result.append(f"{product} {temp_df.iloc[0, 3]} {temp_df.iloc[0, -1]}")



