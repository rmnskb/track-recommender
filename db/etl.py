import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


class ExtractTransformLoad:
    _db_user = os.environ.get('POSTGRES_USER')
    _db_passwd = os.environ.get('POSTGRES_PASSWORD')
    _db = os.environ.get('POSTGRES_DB')
    _source_url = 'hf://datasets/maharshipandya/spotify-tracks-dataset/dataset.csv'
    _sql_engine = create_engine(f'postgresql://{_db_user}:{_db_passwd}@localhost:5432/{_db}')

    def __init__(self):
        self._df = pd.DataFrame()
        self._tracks = pd.DataFrame()
        self._albums = pd.DataFrame()
        self._artists = pd.DataFrame()
        self._tracks_artists = pd.DataFrame()

    def _fetch_data(self):
        self._df = pd.read_csv(self.__class__._source_url)

    @staticmethod
    def _preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        df = (
            df
            .drop(columns=['Unnamed: 0'])
            .dropna()
            .drop_duplicates(subset='track_id', keep='first', inplace=False)
        )

        return df

    def _normalise_tables(self) -> None:
        self._fetch_data()
        df = self._preprocess_data(self._df)

        albums = pd.DataFrame(
            df['album_name']
            .drop_duplicates()
        ).rename({'album_name': 'album'}, axis=1).reset_index(drop=True)

        artists = pd.DataFrame(
            df
            .artists
            .str
            .split(';')
            .explode()
            .drop_duplicates()
        ).rename({'artists': 'artist'}, axis=1).reset_index(drop=True)

        albums.insert(loc=0, column='album_id', value=pd.Series(range(1, len(albums) + 1), dtype='Int64'))

        artists.insert(loc=0, column='artist_id', value=pd.Series(range(1, len(artists) + 1), dtype='Int64'))

        tracks_artists = (
            df[['track_id', 'artists']]
        )
        tracks_artists.loc[:, 'artists'] = tracks_artists['artists'].str.split(';')
        tracks_artists = tracks_artists.explode('artists').rename({'artists': 'artist'}, axis=1)
        tracks_artists = pd.merge(
            tracks_artists
            , artists
            , on='artist'
            , how='left'
        )[['track_id', 'artist_id']]

        tracks = pd.merge(
            df
            , albums
            , left_on='album_name'
            , right_on='album'
        ).drop(['artists', 'album_name', 'album'], axis=1)

        self._tracks = tracks
        self._albums = albums
        self._artists = artists
        self._tracks_artists = tracks_artists

    def populate_database(self) -> None:
        self._normalise_tables()
        engine = self.__class__._sql_engine

        table_mappings = {
            'tracks': self._tracks
            , 'albums': self._albums
            , 'artists': self._artists
            , 'tracks_artists': self._tracks_artists
        }

        try:
            with engine.connect() as conn:
                for table_name, dataframe in table_mappings.items():
                    dataframe.to_sql(
                        name=table_name
                        , if_exists='replace'
                        , con=conn
                        , index=False
                    )
        except Exception as e:
            raise e


if __name__ == '__main__':
    etl = ExtractTransformLoad()
    etl.populate_database()
