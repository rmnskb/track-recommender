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

    def __init__(self, reuse_model: bool = True, filename: str = 'kdt.pkl'):
        base_path = os.path.dirname(__file__)
        model_path = os.path.join(base_path, filename)

        if reuse_model and os.path.isfile(model_path):
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
        elif reuse_model and not os.path.isfile(model_path):
            raise FileNotFoundError(f'There is no pickle file in the provided path: {model_path}')
        else:
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

    def recommend(self, ids: list[str], n_recs: int):
        """
        Recommend tracks using KDTree model, bases the recommendations on provided track ids. Please consider
        training the model first before you run this method, unless you have a pickled model in the directory.
        :param ids: list of track ids, please note that you should parse list even if it is one value
        :param n_recs: number of recommendations to return
        :return: ids of the closest neighbours
        """
        if not self.model:
            raise ValueError(f'Recommender model does not exist, please consider training it first using .train()')

        if len(ids) > 1:
            query = f"""
                select *
                from pr_comps 
                where track_id in {tuple(ids)}
            """
        elif len(ids) == 1:
            query = f"""
                select *
                from pr_comps 
                where track_id = '{ids[0]}'
            """
        else:
            raise ValueError(f'ids should be a list of string, you provided {type(ids)}')

        if self.data.empty:
            try:
                with self.__class__._sql_engine.connect() as conn:
                    data = pd.read_sql(query, con=conn).drop(columns=['track_id'])
            except exc.OperationalError as e:
                print(f'Trouble connecting to the database, {e}')
        else:  # self.data is already populated
            data = self.data[self.data['track_id'].isin(ids)]

        kdt = self.model
        recs_idx = kdt.query(data, k=n_recs + 1, return_distance=False)

        return recs_idx[:, 1:]  # don't return the point itself


if __name__ == '__main__':
    recommender = Recommender()
    recommender.train(n_dimensions=6, leaf_size=7)
    recommender.save()
