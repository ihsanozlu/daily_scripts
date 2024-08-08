import psycopg2
from psycopg2 import sql, extras

primary_db_config = {
    "host": "host1",
    "dbname": "dbname1",
    "user": "postgres",
    "password": "password",
    "port": 5432
}

secondary_db_config = {
    "host": "host2",
    "dbname": "dbname1",
    "user": "postgres",
    "password": "password",
    "port": 5432
}

def get_connection(config):
    try:
        return psycopg2.connect(**config)
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        raise

def get_tables(connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT table_catalog, table_schema, table_name
                FROM information_schema.tables
                WHERE table_type = 'BASE TABLE'
                """
            )
            return [(row[0], row[1], row[2]) for row in cursor.fetchall()]
    except psycopg2.Error as e:
        print(f"Error fetching tables: {e}")
        raise

def table_is_empty(connection, table_catalog, table_schema, table_name):
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql.SQL(
                "SELECT EXISTS (SELECT 1 FROM {}.{}.{} LIMIT 1)"
            ).format(
                sql.Identifier(table_catalog),
                sql.Identifier(table_schema),
                sql.Identifier(table_name)
            ))
            return not cursor.fetchone()[0]
    except psycopg2.Error as e:
        print(f"Error checking if table is empty: {e}")
        raise

def copy_data(primary_conn, secondary_conn, table_catalog, table_schema, table_name):
    try:
        with primary_conn.cursor() as primary_cursor, secondary_conn.cursor() as secondary_cursor:
            primary_cursor.execute(sql.SQL("SELECT * FROM {}.{}.{}").format(
                sql.Identifier(table_catalog),
                sql.Identifier(table_schema),
                sql.Identifier(table_name)
            ))
            rows = primary_cursor.fetchall()
            if not rows:
                return
            
            # Get column names
            colnames = [desc[0] for desc in primary_cursor.description]
            # Insert data into secondary
            insert_query = sql.SQL("INSERT INTO {}.{}.{} ({}) VALUES %s").format(
                sql.Identifier(table_catalog),
                sql.Identifier(table_schema),
                sql.Identifier(table_name),
                sql.SQL(', ').join(map(sql.Identifier, colnames))
            )
            extras.execute_values(
                secondary_cursor, insert_query, rows, template=None, page_size=100
            )
            secondary_conn.commit()
    except psycopg2.Error as e:
        print(f"Error copying data for table {table_name}: {e}")
        secondary_conn.rollback()
        raise

def synchronize_databases():
    primary_conn = None
    secondary_conn = None
    try:
        primary_conn = get_connection(primary_db_config)
        secondary_conn = get_connection(secondary_db_config)
        
        primary_tables = get_tables(primary_conn)
        secondary_tables = get_tables(secondary_conn)
        
        # Only consider tables that exist in both databases
        common_tables = set(primary_tables).intersection(secondary_tables)
        for table_catalog, table_schema, table_name in common_tables:
            try:
                if table_is_empty(primary_conn, table_catalog, table_schema, table_name) and table_is_empty(secondary_conn, table_catalog, table_schema, table_name):
                    print(f"Skipping empty table: {table_catalog}.{table_schema}.{table_name}")
                    continue
                if not table_is_empty(primary_conn, table_catalog, table_schema, table_name) and table_is_empty(secondary_conn, table_catalog, table_schema, table_name):
                    print(f"Copying data from {table_catalog}.{table_schema}.{table_name}...")
                    copy_data(primary_conn, secondary_conn, table_catalog, table_schema, table_name)
                    print(f"Data copied for table: {table_catalog}.{table_schema}.{table_name}")
                else:
                    print(f"Skipping table {table_catalog}.{table_schema}.{table_name}, either both are full or secondary is not empty.")
            except Exception as e:
                print(f"Error processing table {table_catalog}.{table_schema}.{table_name}: {e}")
                continue
    except Exception as e:
        print(f"Error during database synchronization: {e}")
    finally:
        if primary_conn:
            primary_conn.close()
        if secondary_conn:
            secondary_conn.close()

if __name__ == "__main__":
    synchronize_databases()

