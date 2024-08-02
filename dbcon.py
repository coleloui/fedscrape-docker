"""connection to PostgreSQL db"""

# package import
import psycopg2

connection = psycopg2.connect(
    "dbname=postgres user=postgres host=database password=test port=5432"
)

cursor = connection.cursor()

cursor.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")

cursor.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))
cursor.execute("SELECT * FROM test;")
print(cursor.fetchone())

cursor.close()
connection.close()
