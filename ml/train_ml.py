import os
import pickle
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, exc
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import KDTree


load_dotenv()


class Recommender:
    _db_user = os.environ.get('POSTGRES_USER')
    _db_passwd = os.environ.get('POSTGRES_PASSWORD')
    _db = os.environ.get('POSTGRES_DB')
    _sql_engine = create_engine(f'postgresql://{_db_user}:{_db_passwd}@localhost:5432/{_db}')

    def __init__(self):
        self.model = None
        self.data = pd.DataFrame()
        try:
            with self.__class__._sql_engine.connect() as conn:
                df = pd.read_sql(
                    "select * from tracks"
                    , con=conn
                )

                self._df = (
                    df
                    .set_index('track_id')
                    .select_dtypes(include=['float64', 'int64'])
                    .drop(columns=['key', 'time_signature'])
                )
        except exc.OperationalError as e:
            print(f'Trouble connecting to the database, {e}')

    @staticmethod
    def _preprocess_data(df: pd.DataFrame, n_components: int = 6) -> pd.DataFrame:
        scaler = StandardScaler()
        pca = PCA()

        df_scaled = pd.DataFrame(
            scaler.fit_transform(X=df)
            , columns=df.columns
            , index=df.index
        )

        p_comps = pd.DataFrame(
            pca.fit_transform(df_scaled)[:, :n_components]
            , columns=[f'PC{i+1}' for i in range(6)]
            , index=df_scaled.index
        )

        return p_comps

    def train(self, n_dimensions: int = 6, leaf_size: int = 7) -> None:
        self.data = self._preprocess_data(self._df, n_components=n_dimensions)

        self.model = KDTree(self.data, leaf_size=leaf_size)

    def save(self):
        with open('kdt.pkl', 'wb') as f:
            pickle.dump(self.model, f)

        try:
            with self.__class__._sql_engine.connect() as conn:
                self.data.to_sql(
                    name='pr_comps'
                    , if_exists='replace'
                    , con=conn
                    , index=True
                    , index_label='track_id'
                )
        except exc.OperationalError as e:
            print(f'Trouble connecting to the database, {e}')


if __name__ == '__main__':
    recommender = Recommender()
    recommender.train(n_dimensions=6, leaf_size=7)

    data = recommender.data
    kdt = recommender.model

    recommender.save()
