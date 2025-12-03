import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="phonebook",
    user="postgres",
    password="52CHINGABOSS52"
)
cur = conn.cursor()

#создает все таблицы и функции если не создали
cur.execute("""
CREATE TABLE IF NOT EXISTS PhoneBook (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL
);
""")

cur.execute("""
CREATE OR REPLACE FUNCTION search_contacts(pattern TEXT)
RETURNS TABLE(id INT, first_name TEXT, phone TEXT)
AS $$
BEGIN
    RETURN QUERY
    SELECT id, first_name, phone
    FROM PhoneBook
    WHERE first_name ILIKE '%' || pattern || '%'
       OR phone ILIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;
""")

cur.execute("""
CREATE OR REPLACE PROCEDURE add_or_update_user(p_name TEXT, p_phone TEXT)
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM PhoneBook WHERE first_name = p_name) THEN
        UPDATE PhoneBook SET phone = p_phone WHERE first_name = p_name;
    ELSE
        INSERT INTO PhoneBook(first_name, phone) VALUES (p_name, p_phone);
    END IF;
END;
$$ LANGUAGE plpgsql;
""")

cur.execute("""
CREATE OR REPLACE PROCEDURE add_many_users(
    names TEXT[],
    phones TEXT[],
    OUT incorrect TEXT[]
)
AS $$
DECLARE
    i INT;
BEGIN
    incorrect := ARRAY[]::TEXT[];
    FOR i IN 1..array_length(names, 1) LOOP
        IF phones[i] !~ '^[0-9]+$' THEN
            incorrect := array_append(incorrect, names[i] || ':' || phones[i]);
            CONTINUE;
        END IF;
        BEGIN
            INSERT INTO PhoneBook(first_name, phone) VALUES (names[i], phones[i]);
        EXCEPTION WHEN unique_violation THEN
            UPDATE PhoneBook SET first_name = names[i] WHERE phone = phones[i];
        END;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
""")

cur.execute("""
CREATE OR REPLACE FUNCTION get_paginated(limit_n INT, offset_n INT)
RETURNS TABLE(id INT, first_name TEXT, phone TEXT)
AS $$
BEGIN
    RETURN QUERY
    SELECT id, first_name, phone FROM PhoneBook ORDER BY id LIMIT limit_n OFFSET offset_n;
END;
$$ LANGUAGE plpgsql;
""")

cur.execute("""
CREATE OR REPLACE PROCEDURE delete_user(key TEXT)
AS $$
BEGIN
    DELETE FROM PhoneBook WHERE first_name = key OR phone = key;
END;
$$ LANGUAGE plpgsql;
""")

conn.commit()

print("Таблица и функции/процедуры созданы")

#тут работа с данными

#добавляет или обновляет пользователя
cur.execute("CALL add_or_update_user(%s, %s)", ('Tarlan', '77001234567'))
conn.commit()
print("Добавлен или обновлен пользователь: Tarlan")

#добавляет много пользователей
names = ['Igor', 'Egor', 'Rustam']
phones = ['77007654321', '7700191031', '77471337312']
cur.execute("CALL add_many_users(%s, %s)", (names, phones))
conn.commit()
print("Добавлены несколько пользователей")

#поиски по шаблону "ar"
cur.execute("SELECT * FROM search_contacts(%s)", ('ar',))
results = cur.fetchall()
print("Результаты поиска по 'ar':", results)

#плагинация и первый 10 записей
cur.execute("SELECT * FROM get_paginated(%s, %s)", (10, 0))
results = cur.fetchall()
print("Первые 10 записей:", results)

#удаляет игоря
cur.execute("CALL delete_user(%s)", ('Igor',))
conn.commit()
print("Удален пользователь: Igor")

#проверяет что игоря удалили
cur.execute("SELECT * FROM search_contacts(%s)", ('Igor',))
results = cur.fetchall()
print("Проверка после удаления 'Igor' (должно быть пусто):", results)

cur.close()
conn.close()
