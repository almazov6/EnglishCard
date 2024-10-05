import psycopg2 as db

conn = db.connect(database="", user="", password="")


def add_word_to_database(user_id, english_word, translate_word):
    with conn.cursor() as cur:
        cur.execute(f"""
        INSERT INTO word_user(user_id, english_word, translate_word)
        VALUES ({user_id}, %s, %s);
        """, (english_word, translate_word))
        conn.commit()


def is_word_in_database(user_id, english_word):
    flag = False
    with conn.cursor() as cur:
        cur.execute(f"""
        SELECT english_word FROM word_user
        WHERE english_word = '{english_word}' AND user_id = {user_id}
        """)
        word = cur.fetchall()
        if len(word) != 0:
            flag = True
    return flag


def add_user(user_id):
    with conn.cursor() as cur:
        cur.execute(f"""
        INSERT INTO users(user_id) VALUES ({user_id});
        """)
        conn.commit()


def users_list():
    with conn.cursor() as cur:
        cur.execute(f"""
        SELECT user_id FROM users
        """)
        users = cur.fetchall()
        return users


def user_id_in_database(user_id):
    flag = False
    for i in range(len(users_list())):
        if user_id in users_list()[i]:
            flag = True
    return flag


def del_word_in_database(user_id, english_word):
    with conn.cursor() as cur:
        cur.execute(f"""
        DELETE FROM word_user WHERE user_id = {user_id}
        AND english_word='{english_word}';
        """)
        conn.commit()


def count_words(user_id):
    with conn.cursor() as cur:
        cur.execute(f"""
        SELECT COUNT(user_id) FROM word_user
        WHERE user_id = {user_id}
        """)
        word = cur.fetchone()
        return word[0]


def random_word(table_name, user_id):
    with conn.cursor() as cur:
        cur.execute(f"""
        SELECT {table_name} FROM word_user
        WHERE user_id = {user_id}
        ORDER BY RANDOM()
        """)
        word = cur.fetchone()
        return ''.join(word)


def translate_word(target_word):
    with conn.cursor() as cur:
        cur.execute(f"""
        SELECT translate_word FROM word_user
        WHERE english_word = '{target_word}'
        """)
        word = cur.fetchone()
        return ''.join(word)


def others_word(target_word, user_id):
    with conn.cursor() as cur:
        arr = []
        i = 0
        while i < 3:
            cur.execute(f"""
            SELECT english_word FROM word_user
            WHERE user_id = {user_id}
            ORDER BY RANDOM()
            """)
            words = cur.fetchone()
            if ''.join(words) not in arr and ''.join(words) != target_word:
                arr.append(''.join(words))
                i += 1
        return arr


def start_word():
    with conn.cursor() as cur:
        cur.execute(f"""
        SELECT english_word, translate_word FROM words
        """)
        word = cur.fetchall()
        return word
