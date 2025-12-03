import psycopg2
from config import load_config
#подключаемся к базе и создем таблицу
def create_table():
    config = load_config()

    conn = psycopg2.connect(**config)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS PhoneBook (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            phone VARCHAR(20) UNIQUE NOT NULL
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    create_table()
