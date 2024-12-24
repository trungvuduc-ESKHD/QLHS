import sqlite3
import datetime
import hashlib

class BookDAL:
    def __init__(self, db_name='document_management.db'):
        self.db_name = db_name
    
    def connect_db(self):
        return sqlite3.connect(self.db_name, check_same_thread=False)
    
    def create_table(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                author TEXT NOT NULL,
                price TEXT NOT NULL,
                category TEXT NOT NULL,
                file_path TEXT,
                created_at DATETIME
            )
        ''')
        
        # Kiểm tra xem cột 'created_at' đã tồn tại chưa
        cursor.execute("PRAGMA table_info(books)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'created_at' not in columns:
            cursor.execute("ALTER TABLE books ADD COLUMN created_at DATETIME")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS book_tags (
                book_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                FOREIGN KEY (book_id) REFERENCES books(id),
                FOREIGN KEY (tag_id) REFERENCES tags(id),
                PRIMARY KEY (book_id, tag_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                value TEXT,
                FOREIGN KEY (book_id) REFERENCES books(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                shared_with INTEGER NOT NULL,
                permission TEXT NOT NULL,
                share_code TEXT NOT NULL UNIQUE,
                 FOREIGN KEY (book_id) REFERENCES books(id),
                 FOREIGN KEY (user_id) REFERENCES users(id),
                 FOREIGN KEY (shared_with) REFERENCES users(id)
                 
            )
        ''')
        cursor.execute('''
             CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                created_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(id)
             )
        ''')
        conn.commit()
        conn.close()

    def insert_book(self, name, author, price, category, file_path, created_at):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO books (name, author, price, category, file_path, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, author, price, category, file_path, created_at))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting book: {e}")
        finally:
            conn.close()

    def update_book(self, book_id, name, author, price, category, file_path):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE books
            SET name = ?, author = ?, price = ?, category = ?, file_path = ?
            WHERE id = ?
        ''', (name, author, price, category, file_path, book_id))
        conn.commit()
        conn.close()

    def delete_book(self, book_id):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM books
            WHERE id = ?
        ''', (book_id,))
        conn.commit()
        conn.close()

    def get_books(self, search_text, filter_category):
        conn = self.connect_db()
        cursor = conn.cursor()

        query = "SELECT * FROM books WHERE name LIKE ?"
        params = [f'%{search_text}%']

        if filter_category != "All":
            query += " AND category = ?"
            params.append(filter_category)

        cursor.execute(query, params)
        books = cursor.fetchall()
        conn.close()

        return books
    def get_books_advance(self, search_text, search_code, search_unit, filter_category, filter_date_from, filter_date_to):
        conn = self.connect_db()
        cursor = conn.cursor()

        query = "SELECT * FROM books WHERE 1=1"
        params = []
        if search_text:
            query += " AND name LIKE ?"
            params.append(f'%{search_text}%')
        
        if search_code:
            query += " AND price LIKE ?"
            params.append(f'%{search_code}%')
        
        if search_unit:
             query += " AND author LIKE ?"
             params.append(f'%{search_unit}%')

        if filter_category != "All":
            query += " AND category = ?"
            params.append(filter_category)
            
        if filter_date_from:
            query += " AND created_at >= ?"
            params.append(filter_date_from)
        if filter_date_to:
             query += " AND created_at <= ?"
             params.append(datetime.datetime.combine(filter_date_to, datetime.time.max))

        cursor.execute(query, params)
        books = cursor.fetchall()
        conn.close()

        return books
    def insert_user(self, username, password):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (username, password)
                VALUES (?, ?)
            ''', (username, hashed_password))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting user: {e}")
            return False
        finally:
            conn.close()
        return True
    def get_user(self, username, password):
        conn = self.connect_db()
        cursor = conn.cursor()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute('''
            SELECT * FROM users
            WHERE username = ? AND password = ?
        ''', (username, hashed_password))
        user = cursor.fetchone()
        conn.close()
        return user
    def get_user_by_id(self, id):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM users
            WHERE id = ?
        ''', (id,))
        user = cursor.fetchone()
        conn.close()
        return user
    def update_user_password(self, user_id, new_password):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            cursor.execute('''
                UPDATE users
                SET password = ?
                WHERE id = ?
            ''', (hashed_password, user_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating user password: {e}")
            return False
        finally:
            conn.close()
    def get_all_users(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM users
        ''')
        users = cursor.fetchall()
        conn.close()
        return users
    def update_user_role(self, user_id, new_role):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users
                SET role = ?
                WHERE id = ?
            ''', (new_role, user_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating user role: {e}")
            return False
        finally:
            conn.close()
    def delete_user(self, user_id):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM users
                WHERE id = ?
            ''', (user_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting user: {e}")
            return False
        finally:
            conn.close()
    def insert_message(self, user_id, message, created_at):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (user_id, message, created_at)
                VALUES (?, ?, ?)
            ''', (user_id, message, created_at))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error insert message: {e}")
            return None
        finally:
             conn.close()
    def get_messages(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('''
           SELECT messages.message, users.username ,messages.created_at FROM messages
           JOIN users ON users.id = messages.user_id
        ''')
        messages = cursor.fetchall()
        conn.close()
        return messages
    def insert_tag(self, name):
        try:
             conn = self.connect_db()
             cursor = conn.cursor()
             cursor.execute('''
                 INSERT INTO tags (name)
                 VALUES (?)
             ''', (name,))
             conn.commit()
             return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error insert tag: {e}")
            return None
        finally:
            conn.close()
    def get_tag_by_name(self,name):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('''
           SELECT * FROM tags WHERE name = ?
        ''',(name,))
        tag = cursor.fetchone()
        conn.close()
        return tag
    def insert_book_tag(self,book_id, tag_id):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute('''
               INSERT INTO book_tags (book_id, tag_id)
               VALUES (?,?)
           ''',(book_id,tag_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
             print(f"Error insert book tag: {e}")
             return False
        finally:
            conn.close()
    def get_book_tags(self,book_id):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT tags.name FROM tags
            INNER JOIN book_tags ON tags.id = book_tags.tag_id
            WHERE book_tags.book_id = ?
        ''',(book_id,))
        tags = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tags
    def insert_metadata(self, book_id, name, value):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO metadata (book_id, name, value)
                VALUES (?,?,?)
            ''',(book_id, name, value))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error inserting metadata: {e}")
            return False
        finally:
            conn.close()
    def get_metadata(self,book_id):
         conn = self.connect_db()
         cursor = conn.cursor()
         cursor.execute('''
            SELECT name, value FROM metadata WHERE book_id = ?
        ''',(book_id,))
         data = cursor.fetchall()
         conn.close()
         return data
    def insert_share(self, book_id, user_id, shared_with, permission, share_code):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute('''
               INSERT INTO shares (book_id, user_id, shared_with, permission, share_code)
               VALUES (?,?,?,?,?)
           ''',(book_id, user_id, shared_with, permission, share_code))
            conn.commit()
            return True
        except sqlite3.Error as e:
             print(f"Error insert share: {e}")
             return False
        finally:
            conn.close()
    def get_share_by_code(self, share_code):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM shares WHERE share_code = ?
        ''',(share_code,))
        data = cursor.fetchone()
        conn.close()
        return data