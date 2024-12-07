import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, exc

load_dotenv()


class DB:
    _db_user = os.environ.get('POSTGRES_USER')
    _db_passwd = os.environ.get('POSTGRES_PASSWORD')
    _db = os.environ.get('POSTGRES_DB')
    _sql_engine = create_engine(f'postgresql://{_db_user}:{_db_passwd}@localhost:5432/{_db}')

    @staticmethod
    def _build_filters(
            filters: dict[str, str | list[str] | float | list[float]]
    ) -> tuple[str, dict[str, str | list[str] | float | list[float]]]:
        """Build the where clause for the sql query that handles the logic"""
        conditions = []
        params = {}

        if filters:
            for col, val in filters.items():
                if isinstance(val, (int, float, str)):
                    conditions.append(f"col = %({col})s")
                    params[col] = val
                elif isinstance(val, list):
                    if len(val) == 1:
                        conditions.append(f"{col} = %({col})s")
                        params[col] = val[0]
                    elif len(val) > 1:
                        conditions.append(f"{col} in %({col}_tuple)s")
                        params[f"{col}_tuple"] = tuple(val)
                elif val is None:
                    conditions.append(f"{col} is null")

        where = 'where ' + 'and '.join(conditions) if conditions else ''

        return where, params

    @classmethod
    def query_table(
            cls
            , table_name: str
            , columns: list[str] = None
            , filters: dict[str, str | list[str] | float | list[float] | None] = None
            , order_by: str | list[str] = None
            , limit: int = None
    ) -> pd.DataFrame:
        """
        A wrapper for pandas' sql api, allows you to query database via python interface
        :param table_name: Table Name, required parameter
        :param columns: a list of columns to query, please parse a list even if you want one column, * if None, optional
        :param filters: filters to be used with the query,
            pass the dictionary with columns as keys and values as values, use None for nulls
        :param order_by: columns to sort by
        :param limit: limit of rows to return
        :return: pandas' Dataframe with the result, empty df if no result
        """
        # TODO: check if table exists in the db

        if not columns:
            columns = '*'
        elif len(columns) == 1:
            columns = columns[0]
        elif len(columns) > 1:
            columns = ', '.join(columns)

        where, params = cls._build_filters(filters=filters)

        if order_by:
            sort = 'order by ' + ', '.join(order_by) if isinstance(order_by, list) else order_by
        else:
            sort = ''

        query = f"""
            select {columns}
            from {table_name}
            {where}
            {sort}
            {'limit ' + str(limit) if limit else ''}
        """

        try:
            with cls._sql_engine.connect() as conn:
                data = pd.read_sql(
                    sql=query
                    , con=conn
                    , params=params
                )
        except exc.OperationalError as e:
            print(f'Trouble connecting to the database, {e}')
            data = pd.DataFrame()

        return data


if __name__ == '__main__':
    db_handler = DB()
    ids = ['5SuOikwiRyPMVoIQDJUgSV', '1iJBSr7s7jYXzM8EGcbK5b']
    data = db_handler.query_table(
                table_name='tracks'
                , filters={
                    'track_id': ids
                }
            )

    print(data)
