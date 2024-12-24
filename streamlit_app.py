import streamlit as st
import dataController as dc
import os
from PIL import Image
import PyPDF2
import io
import base64
import datetime
import hashlib
import uuid
import requests
from streamlit_option_menu import option_menu
import pdfplumber

MS_TEAMS_WEBHOOK_URL = "https://erfxxam.webhook.office.com/webhookb2/4855e595-4013-44b5-97a5-d815430d7e4b@f29c254b-53da-4110-abde-498f85d6ebaf/IncomingWebhook/9800667b5556458bb99e136cda97b4c2/861054b1-b771-4ed9-8a56-b0a0c223585b/V2Ag2a04pEno54Oj5C4uo2HM5ICZ4WAfNkKi1kc_u6vYs1"

if "edit_key" not in st.session_state:
    st.session_state.edit_key = None
    
def init_database():
    dc.create_table()

def main():
    st.set_page_config(page_title="Quản Lý Hồ Sơ Doanh Nghiệp", page_icon="🌎", layout="wide")
    st.sidebar.image("images/logo2.png")
    st.sidebar.title("📚 QUẢN LÝ HỒ SƠ")

    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user:
         if st.session_state.user[3] == 'admin':
              with st.sidebar:
                menu_selection = option_menu("Chọn chức năng", 
                    ["Thêm Hồ Sơ", "Danh Sách Hồ Sơ", "Quản lý người dùng", "Đổi mật khẩu", "Chat", "Đăng xuất"],
                     icons=['file-earmark-plus','list-task', 'people', 'key', 'chat-dots','box-arrow-left'],
                    menu_icon="cast", default_index=0,
                    styles={
                        "container": {"padding": "0!important", "background-color": "#fafafa"},
                        "icon": {"color": "orange", "font-size": "25px"}, 
                        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                        "nav-link-selected": {"background-color": "gray"},
                    },
                )
         else:
              with st.sidebar:
                menu_selection = option_menu("Chọn chức năng", 
                    ["Danh Sách Hồ Sơ", "Đổi mật khẩu", "Chat", "Đăng xuất"],
                     icons=['list-task', 'key', 'chat-dots','box-arrow-left'],
                    menu_icon="cast", default_index=0,
                    styles={
                        "container": {"padding": "0!important", "background-color": "#fafafa"},
                        "icon": {"color": "orange", "font-size": "25px"}, 
                        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                        "nav-link-selected": {"background-color": "gray"},
                    },
                 )
         if menu_selection == "Đăng xuất":
             del st.session_state.user
             st.experimental_rerun()
         elif menu_selection == "Thêm Hồ Sơ":
             add_document_page()
         elif menu_selection == "Danh Sách Hồ Sơ":
             list_documents_page()
         elif menu_selection == "Quản lý người dùng":
             user_management_page()
         elif menu_selection == "Đổi mật khẩu":
             change_password_page()
         elif menu_selection == "Chat":
              chat_widget()
    else:
         with st.sidebar:
             menu_selection = option_menu("Chọn Chức Năng",
                                    ["Đăng nhập", "Đăng ký"])
         if menu_selection == "Đăng nhập":
             login_page()
         elif menu_selection == "Đăng ký":
             register_page()
def login_page():
    st.title("Đăng nhập")
    with st.form(key="login_form"):
        username = st.text_input("Tên đăng nhập")
        password = st.text_input("Mật khẩu", type="password")
        login_button = st.form_submit_button("Đăng nhập")

        if login_button:
            user = dc.getUser(username, password)
            if user:
                st.session_state.user = user
                st.success("Đăng nhập thành công")
                st.experimental_rerun()
            else:
                 st.error("Tên đăng nhập hoặc mật khẩu không đúng")
def register_page():
    st.title("Đăng ký")
    with st.form(key="register_form"):
         username = st.text_input("Tên đăng nhập")
         password = st.text_input("Mật khẩu", type="password")
         register_button = st.form_submit_button("Đăng ký")
    
         if register_button:
             if username and password:
                if dc.insertUser(username, password):
                     st.success("Đăng ký thành công, vui lòng đăng nhập")
                     send_teams_notification(f"Người dùng mới đăng ký: {username}")
                else:
                    st.error("Tên đăng nhập đã tồn tại")
             else:
                 st.error("Vui lòng nhập tên đăng nhập và mật khẩu")
def change_password_page():
    st.title("Đổi mật khẩu")
    with st.form(key="change_password_form"):
        old_password = st.text_input("Mật khẩu cũ", type="password")
        new_password = st.text_input("Mật khẩu mới", type="password")
        confirm_password = st.text_input("Xác nhận mật khẩu mới", type="password")
        change_button = st.form_submit_button("Đổi mật khẩu")
        if change_button:
            if old_password and new_password and confirm_password:
                user = dc.getUser(st.session_state.user[1],old_password)
                if user:
                     if new_password == confirm_password:
                        if dc.updateUserPassword(st.session_state.user[0], new_password):
                            st.success("Đổi mật khẩu thành công, vui lòng đăng nhập lại")
                            del st.session_state.user
                            st.experimental_rerun()
                        else:
                            st.error("Lỗi khi đổi mật khẩu")
                     else:
                         st.error("Mật khẩu mới không khớp")
                else:
                    st.error("Mật khẩu cũ không đúng")
            else:
                 st.error("Vui lòng nhập đủ thông tin")
def user_management_page():
    st.header("Quản lý người dùng")
    users = dc.getAllUsers()
    if users:
        for user in users:
           if user[0] != st.session_state.user[0]:
            with st.expander(f"**{user[1]}** - Role: {user[3]}"):
                st.write(f"**ID:** {user[0]}")
                col1, col2 = st.columns(2)
                with col1:
                    new_role = st.selectbox("Phân quyền", ["user", "admin"], key=f"role_{user[0]}", index=["user", "admin"].index(user[3]))
                    if st.button("Cập nhật quyền", key=f"update_role_{user[0]}"):
                        if dc.updateUserRole(user[0], new_role):
                            st.success("Cập nhật quyền thành công")
                            st.experimental_rerun()
                        else:
                            st.error("Lỗi khi cập nhật quyền")
                with col2:
                    if st.button("Đổi mật khẩu", key=f"change_pass_{user[0]}"):
                        with st.form(key=f"change_pass_form_{user[0]}"):
                            new_password = st.text_input("Mật khẩu mới", type="password", key=f"new_pass_{user[0]}")
                            confirm_password = st.text_input("Xác nhận mật khẩu mới", type="password",key=f"confirm_pass_{user[0]}")
                            submit_button = st.form_submit_button("Đổi mật khẩu")
                            if submit_button:
                                if new_password and confirm_password:
                                     if new_password == confirm_password:
                                        if dc.updateUserPassword(user[0], new_password):
                                             st.success("Đổi mật khẩu thành công")
                                        else:
                                            st.error("Lỗi khi đổi mật khẩu")
                                     else:
                                         st.error("Mật khẩu mới không khớp")
                                else:
                                    st.error("Vui lòng nhập đủ thông tin")
                    if st.button("Xóa người dùng", key=f"delete_user_{user[0]}"):
                        if dc.deleteUser(user[0]):
                            st.success(f"Xóa người dùng {user[1]} thành công")
                            send_teams_notification(f"User {user[1]} đã bị xóa.")
                            st.experimental_rerun()
                        else:
                            st.error(f"Lỗi khi xóa người dùng {user[1]}")
    else:
        st.info("Không có user nào")
def add_document_page():
    if st.session_state.user and st.session_state.user[3] == 'admin':
      st.header("🛒 Thêm Hồ Sơ Mới")
      with st.form(key='add_document_form'):
          col1, col2 = st.columns(2)
          with col1:
              doc_name = st.text_input("Tên tài liệu", placeholder="Nhập tên tài liệu")
              doc_unit = st.text_input("Đơn vị ban hành", placeholder="Nhập đơn vị ban hành")
          with col2:
              doc_code = st.text_input("Mã tài liệu", placeholder="Nhập mã tài liệu")
              doc_category = st.selectbox("Loại tài liệu",
                                          ["01-Hồ Sơ Pháp Lý", "02-Hồ Sơ Dự Án", "03-Hồ Sơ Nội Bộ", "04-Hợp Đồng"])
          uploaded_file = st.file_uploader("Tải file đính kèm",
                                           type=['pdf', 'docx', 'txt', 'xlsx', 'jpg', 'png'])
          doc_date = st.date_input("Ngày ban hành",key = "doc_date")
          submit_button = st.form_submit_button(label="✔️ Thêm Hồ Sơ")
          if submit_button:
              if doc_name and doc_unit and doc_code and doc_date:
                  file_path = None
                  if uploaded_file:
                      file_path = os.path.join("uploads", uploaded_file.name)
                      os.makedirs("uploads", exist_ok=True)
                      with open(file_path, "wb") as f:
                          f.write(uploaded_file.getbuffer())
                  dc.insertBook(doc_name, doc_unit, doc_code, doc_category, file_path)
                  st.success("Hồ sơ đã được thêm thành công!")
                  send_teams_notification(f"Hồ sơ mới đã được thêm: {doc_name}")
              else:
                  st.error("Vui lòng điền đầy đủ thông tin")
    else:
        st.error("Bạn không có quyền truy cập trang này")

def list_documents_page():
    st.header("Danh Sách Hồ Sơ")

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        search_term = st.text_input("Tìm kiếm theo tên", placeholder="Nhập từ khóa", key="search_term")
        search_code = st.text_input("Tìm kiếm theo mã", placeholder="Nhập mã", key="search_code")
        search_unit = st.text_input("Tìm kiếm theo đơn vị", placeholder="Nhập đơn vị", key="search_unit")
    with col2:
        
        filter_category = st.selectbox("Lọc theo loại", ["All", "01-Hồ Sơ Pháp Lý", "02-Hồ Sơ Dự Án", "03-Hồ Sơ Nội Bộ", "04-Hợp Đồng"], key="filter_category")
        filter_date_from = st.date_input("Lọc theo ngày tạo từ",key="filter_date_from")
        filter_date_to = st.date_input("Lọc theo ngày tạo đến", key="filter_date_to")

    
    with col3:
        if st.button("Áp dụng bộ lọc", key="filter_btn"):
             st.session_state.filter_applied = True
        if st.button("Xóa bộ lọc", key="clear_filter_btn"):
            st.session_state.filter_applied = False
            st.experimental_set_query_params(
                search_term = "",
                search_code = "",
                search_unit = "",
                filter_category = "All",
                filter_date_from = None,
                filter_date_to = None
            )
            
            st.experimental_rerun()

    if "filter_applied" not in st.session_state:
          st.session_state.filter_applied = False
    
    if st.session_state.filter_applied :
        query_params = {
            "search_term": st.session_state.search_term if "search_term" in st.session_state else "",
             "search_code": st.session_state.search_code if "search_code" in st.session_state else "",
              "search_unit": st.session_state.search_unit if "search_unit" in st.session_state else "",
            "filter_category": st.session_state.filter_category if "filter_category" in st.session_state else "All",
            "filter_date_from": st.session_state.filter_date_from if "filter_date_from" in st.session_state else None,
            "filter_date_to": st.session_state.filter_date_to if "filter_date_to" in st.session_state else None,
        }
    else:
       query_params = {
            "search_term": "",
             "search_code": "",
              "search_unit": "",
            "filter_category": "All",
            "filter_date_from": None,
            "filter_date_to": None,
        }
        
    all_books = dc.getBooksAdvance(
        query_params["search_term"],
        query_params["search_code"],
        query_params["search_unit"],
        query_params["filter_category"],
         query_params["filter_date_from"],
          query_params["filter_date_to"],
          )

    categories = set([book[4] for book in all_books])
    
    if categories:
        tabs = st.tabs(list(categories))
    
        for i, category in enumerate(categories):
            with tabs[i]:
                bookList = [book for book in all_books if book[4] == category]
                if bookList:
                    for book in bookList:
                        with st.expander(f"**{book[1]}** - Mã: {book[3]}"):
                            st.write(f"**Đơn vị ban hành:** {book[2]}")
                            st.write(f"**Loại tài liệu:** {book[4]}")
                            if st.session_state.user[3] == 'admin':
                                action_col1, action_col2 = st.columns(2)
                                with action_col1:
                                    if st.button(f"Sửa #{book[0]}", key=f"edit_{book[0]}"):
                                        st.session_state.edit_key = book[0]
                                        
                                with action_col2:
                                    if st.button(f"Xóa #{book[0]}", key=f"delete_{book[0]}"):
                                        dc.deleteBook(book[0])
                                        st.experimental_rerun()
                            if book[5] and os.path.exists(book[5]):
                                
                                if st.button(f"Xem trước #{book[0]}", key=f"preview_{book[0]}"):
                                    with st.form(key=f"preview_form_{book[0]}"):
                                      if st.form_submit_button("Xem trước"):
                                          with st.container():
                                            file_extension = os.path.splitext(book[5])[1].lower()
                                            st.write(f"file extenstion: {file_extension}")
                                            if file_extension == '.pdf':
                                                try:
                                                    with open(book[5], "rb") as f:
                                                        pdf_data = f.read()
                                                        base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
                                                        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf" sandbox></iframe>'
                                                        st.markdown(pdf_display, unsafe_allow_html=True)
                                                except Exception as e:
                                                    st.error(f"Lỗi khi xem trước PDF: {e}")
                                            elif file_extension in ['.jpg', '.jpeg', '.png']:
                                                 try:
                                                     image = Image.open(book[5])
                                                     st.image(image)
                                                 except Exception as e:
                                                     st.error(f"Lỗi khi xem trước ảnh: {e}")
                                            elif file_extension in ['.txt']:
                                                try:
                                                    with open(book[5], "r", encoding="utf-8") as file:
                                                        content = file.read()
                                                        st.code(content, language='text')
                                                except Exception as e:
                                                     st.error(f"Lỗi khi xem trước text: {e}")
                                            else:
                                                st.warning("Không hỗ trợ xem trước loại file này.")
                            if book[5] and os.path.exists(book[5]):
                                 with open(book[5], "rb") as file:
                                    st.download_button(
                                        label="Tải file đính kèm",
                                        data=file,
                                        file_name=os.path.basename(book[5]),
                                        key=f"download_{book[0]}"
                                    )
                if st.session_state.edit_key:
                    book_to_edit = next((b for b in bookList if b[0] == st.session_state.edit_key), None)
                    if book_to_edit:
                         edit_document(book_to_edit)
    else:
         st.info("Không có dữ liệu nào phù hợp với bộ lọc")
            
def edit_document(book):
        st.header("Chỉnh Sửa Hồ Sơ")
        if "edit_data" not in st.session_state:
             st.session_state.edit_data = {
                 "doc_name": book[1],
                 "doc_unit": book[2],
                 "doc_code": book[3],
                 "doc_category": book[4],
                 "file_path": book[5],
                 "book_id": book[0]
                }
        with st.form(key=f'edit_document_form_{book[0]}'):  # Key duy nhất
                st.session_state.edit_data["doc_name"] = st.text_input("Tên tài liệu", value=st.session_state.edit_data["doc_name"])
                st.session_state.edit_data["doc_unit"] = st.text_input("Đơn vị ban hành", value=st.session_state.edit_data["doc_unit"])
                st.session_state.edit_data["doc_code"] = st.text_input("Mã tài liệu", value=st.session_state.edit_data["doc_code"])
                st.session_state.edit_data["doc_category"] = st.selectbox(
                    "Loại tài liệu",
                    ["01-Hồ Sơ Pháp Lý", "02-Hồ Sơ Dự Án", "03-Hồ Sơ Nội Bộ", "04-Hợp Đồng"],
                    index=["01-Hồ Sơ Pháp Lý", "02-Hồ Sơ Dự Án", "03-Hồ Sơ Nội Bộ", "04-Hợp Đồng"].index(st.session_state.edit_data["doc_category"])
                )
                if st.session_state.user[3] == 'admin':
                    uploaded_file = st.file_uploader("Tải file đính kèm mới", type=['pdf', 'docx', 'txt', 'xlsx', 'jpg', 'png'])
                else:
                    st.write("Bạn không có quyền thay đổi file")
                    uploaded_file = None
                submit_button = st.form_submit_button(label="Cập Nhật Hồ Sơ")

                if submit_button:
                    file_path = st.session_state.edit_data["file_path"]
                    if uploaded_file:
                        file_path = os.path.join("uploads", uploaded_file.name)
                        os.makedirs("uploads", exist_ok=True)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        st.session_state.edit_data["file_path"] = file_path

                    dc.updateBook(
                        st.session_state.edit_data["book_id"],
                        st.session_state.edit_data["doc_name"],
                        st.session_state.edit_data["doc_unit"],
                        st.session_state.edit_data["doc_code"],
                        st.session_state.edit_data["doc_category"],
                        st.session_state.edit_data["file_path"]
                    )
                    st.success("Hồ sơ đã được cập nhật thành công!")
                    st.session_state.edit_key = None
                    del st.session_state.edit_data
                    st.experimental_rerun()
def send_teams_notification(message):
    if MS_TEAMS_WEBHOOK_URL:
       payload = {
        "text": message
        }
       requests.post(MS_TEAMS_WEBHOOK_URL, json=payload)
def chat_widget():
    st.header("Chat")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    users = dc.getAllUsers()
    if st.session_state.user[3] == 'admin':
        user_chat = st.selectbox("Chọn user", users, format_func=lambda user: user[1], key="user_select")
        if user_chat:
           messages = [(message, username, created_at) for message, username, created_at in dc.getMessages() if username == user_chat[1]]
        else:
            messages = []
    else:
        messages = [(message, username, created_at) for message, username, created_at in dc.getMessages() if username == st.session_state.user[1]]
    with st.form(key="chat_form"):
        if st.session_state.user[3] == 'admin' and user_chat:
            message = st.text_input("Nhập tin nhắn", key='chat_input')
            send_button = st.form_submit_button("Gửi")
            if send_button and message:
                dc.insertMessage(st.session_state.user[0], message)
                send_teams_notification(f"{st.session_state.user[1]} đã nhắn: {message}")
                st.experimental_rerun()
        elif st.session_state.user:
            message = st.text_input("Nhập tin nhắn", key='chat_input')
            send_button = st.form_submit_button("Gửi")
            if send_button and message:
                dc.insertMessage(st.session_state.user[0], message)
                send_teams_notification(f"{st.session_state.user[1]} đã nhắn: {message}")
                st.experimental_rerun()
        else:
            st.write("Bạn chưa đăng nhập")
    if messages:
        with st.container():
             for message, username, created_at in messages:
                st.write(f"**{username}:** {message} - {created_at}")
if __name__ == "__main__":
    main()
