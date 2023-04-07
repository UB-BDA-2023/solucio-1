import psycopg2
import os


class Timescale:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.environ.get("TS_HOST"),
            port=os.environ.get("TS_PORT"),
            user=os.environ.get("TS_USER"),
            password=os.environ.get("TS_PASSWORD"),
            database=os.environ.get("TS_DBNAME"))
        self.cursor = self.conn.cursor()
        
    def getCursor(self):
            return self.cursor

    def close(self):
        self.cursor.close()
        self.conn.close()
    
    def ping(self):
        return self.conn.ping()
    
    def execute(self, query, fetch=False):
        self.cursor.execute(query)
        if fetch:
            return self.cursor.fetchall()
        self.conn.commit()
    
    def delete(self, table):
        self.cursor.execute("DELETE FROM " + table)
        self.conn.commit()
        
    def generate_insert_query(self, table_name, data):
        if isinstance(data, dict):
            columns = []
            values = []

            for key, value in data.items():
                if value is not None:
                    columns.append(key)
                    if isinstance(value, str):
                        values.append(f"'{value}'")
                    else:
                        values.append(str(value))

            print(columns)
            print(values)
            columns_str = ", ".join(columns)
            values_str = ", ".join(values)

        elif hasattr(data, '__dict__'):
            columns = []
            values = []

            for key, value in data.__dict__.items():
                if value is not None:
                    columns.append(key)
                    if isinstance(value, str):
                        values.append(f"'{value}'")
                    else:
                        values.append(str(value))

            columns_str = ", ".join(columns)
            values_str = ", ".join(values)

        else:
            raise ValueError("Data must be a dictionary or a class with __dict__ attribute.")

        return f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str})"


        
    def apply_migrations(self, conn):
        migrations_dir = os.path.join(os.getcwd(), 'timescale-migrations')
        migration_files = sorted(os.listdir(migrations_dir))
        print("Found migrations: " + str(migration_files))
        for migration_file in migration_files:
            if migration_file.endswith('.sql'):
                with open(os.path.join(migrations_dir, migration_file), 'r') as f:
                    print("Applying migration: " + migration_file)
                    migration_sql = f.read()
                    cursor = conn.cursor()
                    
                    try:
                        if "-- transactional: false" in migration_sql:
                            conn.set_session(autocommit=True)
                            cursor.execute(migration_sql)
                            conn.set_session(autocommit=False)
                        else:
                            cursor.execute("BEGIN;")
                            cursor.execute(migration_sql)
                            cursor.execute("COMMIT;")
                    except Exception as e:
                        print("Error applying migration: " + str(e))
                        conn.rollback()
                        
                    cursor.close()
                    conn.commit()

# Apply the migrations only once
timescale_client = Timescale()
# Only to debug it easier, we delete the tables first
# timescale_client.execute("DROP TABLE IF EXISTS sensor_data CASCADE")
timescale_client.apply_migrations(timescale_client.conn)
         
