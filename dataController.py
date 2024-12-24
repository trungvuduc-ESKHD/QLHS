from dal import BookDAL
import datetime
import hashlib
import uuid

book_dal = BookDAL()

def create_table():
    book_dal.create_table()

def insertBook(name, author, price, category, file_path):
    book_dal.insert_book(name, author, price, category, file_path, datetime.datetime.now())

def updateBook(book_id, name, author, price, category, file_path):
    book_dal.update_book(book_id, name, author, price, category, file_path)

def deleteBook(book_id):
    book_dal.delete_book(book_id)

def getBooks(search_text, filter_category):
    return book_dal.get_books(search_text, filter_category)

def getBooksAdvance(search_text, search_code, search_unit, filter_category, filter_date_from, filter_date_to):
    return book_dal.get_books_advance(search_text, search_code, search_unit, filter_category, filter_date_from, filter_date_to)
def insertUser(username, password):
    return book_dal.insert_user(username, password)

def getUser(username, password):
    return book_dal.get_user(username, password)

def getUserById(id):
    return book_dal.get_user_by_id(id)

def updateUserPassword(user_id, new_password):
    hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
    return book_dal.update_user_password(user_id, hashed_password)
def getAllUsers():
    return book_dal.get_all_users()
def updateUserRole(user_id, new_role):
    return book_dal.update_user_role(user_id, new_role)
def deleteUser(user_id):
    return book_dal.delete_user(user_id)
def insertTag(name):
    return book_dal.insert_tag(name)
def getTagByName(name):
    return book_dal.get_tag_by_name(name)
def insertBookTag(book_id, tag_id):
    return book_dal.insert_book_tag(book_id, tag_id)
def getBookTags(book_id):
    return book_dal.get_book_tags(book_id)
def insertMetadata(book_id, name, value):
    return book_dal.insert_metadata(book_id, name, value)
def getMetadata(book_id):
     return book_dal.get_metadata(book_id)
def insertShare(book_id, user_id, shared_with, permission, share_code = None):
      if share_code is None:
          share_code = str(uuid.uuid4())
      return book_dal.insert_share(book_id, user_id, shared_with, permission, share_code)
def getShareByCode(share_code):
    return book_dal.get_share_by_code(share_code)
def insertMessage(user_id, message, created_at):
   return book_dal.insert_message(user_id, message,created_at)
def getMessages():
   return book_dal.get_messages()