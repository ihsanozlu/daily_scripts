import psycopg2
from psycopg2 import sql
import time


def get_connection(dbname):
    return psycopg2.connect(
        dbname=dbname,
        user='postgres',
        password='password',
        host='host',
        port='5432'
    )

def find_tables_without_tablespace(cursor):
    query = sql.SQL("""
        SELECT
            n.nspname AS schema_name,
            c.relname AS table_name
        FROM
            pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            LEFT JOIN pg_tablespace t ON t.oid = c.reltablespace
        WHERE
            c.relkind = 'r' -- 'r' is for ordinary tables
            AND n.nspname NOT IN ('pg_catalog', 'information_schema')
            AND t.spcname IS NULL;
    """)
    cursor.execute(query)
    return cursor.fetchall()

def alter_table_set_tablespace(cursor, schema_name, table_name, tablespace_name):
    alter_query = sql.SQL("ALTER TABLE {}.{} SET TABLESPACE {};").format(
        sql.Identifier(schema_name),
        sql.Identifier(table_name),
        sql.Identifier(tablespace_name)
    )
    cursor.execute(alter_query)

def retry_on_deadlock(func, *args, **kwargs):
    max_retries = 5
    delay = 1  # initial delay in seconds
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except psycopg2.errors.DeadlockDetected:
            if attempt < max_retries - 1:
                print(f"Deadlock detected. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # exponential backoff
            else:
                raise



def main():
    target_tablespace = 'tablespace'  # Set your target tablespace here

    connection = get_connection('postgres')
    connection.autocommit = True
    cursor = connection.cursor()

    cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
    databases = cursor.fetchall()

    for db in databases:
        dbname = db[0]
        db_connection = get_connection(dbname)
        db_connection.autocommit = True
        db_cursor = db_connection.cursor()
        print(f"\nProcessing database: {dbname}")
        
        tables = find_tables_without_tablespace(db_cursor)
        for schema_name, table_name in tables:
            print(f"Setting tablespace for {schema_name}.{table_name} to {target_tablespace}")
            #alter_table_set_tablespace(db_cursor, schema_name, table_name, target_tablespace)
            retry_on_deadlock(alter_table_set_tablespace, db_cursor, schema_name, table_name, target_tablespace)

        
        db_cursor.close()
        db_connection.close()

    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()

