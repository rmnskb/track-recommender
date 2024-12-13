import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, exc
from sqlalchemy.sql import text

load_dotenv()


class DB:
    """
    A class that handles the DB connection and the interactions with it.
    ...

    Attributes
    ----------
    There are none

    Methods
    -------
    db_exists() -> bool:
        Check whether the given schema exists

    table_exists() -> bool:
        Check whether the vien table exists

    query_table() -> pd.DataFrame:
        Query the table and get the results as pandas' DataFrame

    insert_data() -> None:
        Insert the data to the DB

    update_table() -> None:
        Update the table with new values
    """

    _db_user = os.environ.get('POSTGRES_USER')
    _db_passwd = os.environ.get('POSTGRES_PASSWORD')
    _db = os.environ.get('POSTGRES_DB')
    _sql_engine = create_engine(f'postgresql://{_db_user}:{_db_passwd}@pg:5432/{_db}')

    @classmethod
    def db_exists(cls, table_schema: str = 'public') -> bool:
        """Check whether given table schema exists, return boolean"""
        query = f"""
            select exists(
                select 1
                from information_schema.tables
                where table_schema = '{table_schema}'
            )
        """

        try:
            with cls._sql_engine.connect() as conn:
                result = bool(conn.execute(text(query)).fetchone()[0])

                return result
        except exc.OperationalError as e:
            print(f'Trouble connecting to the database, {e}')

        return False

    @classmethod
    def table_exists(cls, table_name: str) -> bool:
        """Check whether given table exists in the public schema, return boolean"""
        query = f"""
            select exists(
                select 1
                from information_schema.tables
                where table_schema = 'public'
                    and table_name = '{table_name}'
            )
        """

        try:
            with cls._sql_engine.connect() as conn:
                result = bool(conn.execute(text(query)).fetchone()[0])

                return result
        except exc.OperationalError as e:
            print(f'Trouble connecting to the database, {e}')

        return False

    @staticmethod
    def _build_filters(
            filters: dict[str, str | list[str] | float | list[float]]
    ) -> tuple[str, dict[str, str | list[str] | float | list[float]]]:
        """
        Build the where clause for the sql query that handles the logic
        :param filters: a key-value pairs of column and the values to filter for
        :return: the string for the where clause in query and the parameters for the sql call
        """
        conditions = []
        params = {}

        if filters:
            for col, val in filters.items():
                if isinstance(val, (int, float, str)):
                    if isinstance(val, str) and '_like' in col:
                        col = col.replace('_like', '')
                        conditions.append(f"lower({col}) like %({col})s")
                        params[col] = f"%{val.lower()}%"
                    else:
                        conditions.append(f"{col} = %({col})s")
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
        if not cls.table_exists(table_name=table_name):
            raise ValueError(f'The table {table_name} does not exist')

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

    @classmethod
    def update_table(
            cls
            , table_name: str
            , values: list[dict[str,]]
            , filters: dict[str, str | list[str] | float | list[float] | None]
    ) -> None:
        """
        A wrapper function for the sql call that allows you to update the table with new values
        :param table_name: table name in the db, mandatory
        :param values: new values to update the table with, mandatory
        :param filters: filters to be used with the query,
            pass the dictionary with columns as keys and values as values, use None for nulls, mandatory, will update
            the whole table otherwise
        :return: void function, updates the table
        """
        if not cls.table_exists(table_name=table_name):
            raise ValueError(f'The table {table_name} does not exist')

        where, params = cls._build_filters(filters=filters)

        if not values:
            raise ValueError(f'You should specify the values you want to update')
        elif not isinstance(values[0], dict):
            raise TypeError(f'Values should be passed as a list with dictionaries')
        else:
            updates = ', '.join(f'{str(values[0].keys())} = %({str(values[0].keys())})s')

        query = f"""
            update {table_name}
            set {updates}
            {where}
        """

        try:
            with cls._sql_engine.connect() as conn:
                for line in values:
                    conn.execute(text(query), **line, **params)

                conn.commit()
        except exc.OperationalError as e:
            print(f'Trouble connecting to the database, {e}')

    @classmethod
    def insert_data(
            cls
            , table_name: str
            , columns: list[str]
            , values: list[dict[str, ]]
    ) -> None:
        """
         wrapper function for the sql call that allows you to insert new data
        :param table_name: table name in the db, mandatory
        :param columns: a list of columns to insert, please parse a list even if you want one column, mandatory
        :param values: a list of dictionaries, where each dictionary represents a new row,
            and each key-value pair a column and a respective value to insert, mandatory
        :return: void function, inserts new values
        """
        if not cls.table_exists(table_name=table_name):
            raise ValueError(f'The table {table_name} does not exist')

        if not columns:
            raise ValueError(f'You should specify the columns where you want to insert your values')
        elif len(columns) == 1:
            columns = columns[0]
        elif len(columns) > 1:
            columns = ', '.join(columns)

        if not values:
            raise ValueError(f'You should specify the values you want to insert')
        elif not isinstance(values[0], dict):
            raise TypeError(f'Values should be passed as a list with dictionaries')
        else:
            inserts = ', '.join('%(' + str(values[0].keys()) + ')s')

        query = f"""
            insert into {table_name}({columns}) values({inserts})
        """

        try:
            with cls._sql_engine.connect() as conn:
                for line in values:
                    conn.execute(text(query), **line)

                conn.commit()
        except exc.OperationalError as e:
            print(f'Trouble connecting to the database, {e}')


if __name__ == '__main__':
    db_handler = DB()
