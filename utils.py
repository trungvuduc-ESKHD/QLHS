from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import dataController as dc

class BookCard(QFrame):
    def __init__(self, BookId, BookName, BookAuthor, BookPrice, BookCategory, mainWindow):
        super().__init__()

        self.BookId, self.BookName, self.BookAuthor, self.BookPrice, self.BookCategory = BookId, BookName, BookAuthor, BookPrice, BookCategory
        self.mainWindow = mainWindow

        self.setStyleSheet("""
            background: #fff;
            border: 1px solid #ccc;
            border-radius: 5px;
            color: #000;
        """)

        layout = QVBoxLayout()
        labelName = QLabel(f"<b>{BookName}</b>")
        labelName.setStyleSheet("""
            border: 0;
            color: red;
            border-bottom: 1px solid #ccc;
            border-radius: 0px;
            padding: 10px 0;
            margin: 0 10px;
        """)
        labelAuthor = QLabel(f"<b>{BookAuthor}</b>")
        labelAuthor.setStyleSheet("""
            border: 0;
            padding: 10px;
        """)
        labelPrice = QLabel(f"<b>{BookPrice}</b>")
        labelPrice.setStyleSheet("""
            border: 0;
            padding: 10px;
        """)
        labelCategory = QLabel(f"<b>{BookCategory}</b>")
        labelCategory.setStyleSheet("""
            border: 0;
            padding: 10px;
        """)

        buttonLayout = QHBoxLayout()
        buttonDelete = QPushButton(text="Delete", clicked=self.deleteBook)
        buttonDelete.setStyleSheet("""
            QPushButton {
                font-size: 11pt;
                color: #000;
                background-color: #fff;
                border-radius: 0px;
                padding: 10px;
                border: 1px solid #ccc;
                border-bottom-right-radius: 5px;
                border-right: 0px;
                border-bottom: 0px;
            }
            QPushButton:hover {
                color: red;
            }
        """)
        buttonDelete.setCursor(Qt.PointingHandCursor)
        buttonEdit = QPushButton(text="Edit", clicked=self.editBook)
        buttonEdit.setStyleSheet("""
            QPushButton {
                font-size: 11pt;
                color: #000;
                background-color: #fff;
                border-radius: 0px;
                padding: 10px;
                border: 1px solid #ccc;
                border-bottom-left-radius: 5px;
                border-left: 0px;
                border-bottom: 0px;
            }
            QPushButton:hover {
                color: red;
            }
        """)
        buttonEdit.setCursor(Qt.PointingHandCursor)

        buttonLayout.addWidget(buttonEdit, stretch=1)
        buttonLayout.addWidget(buttonDelete, stretch=1)
        buttonLayout.setSpacing(0)

        layout.addWidget(labelName)
        layout.addWidget(labelAuthor)
        layout.addWidget(labelPrice)
        layout.addWidget(labelCategory)
        layout.addLayout(buttonLayout)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def deleteBook(self):
        dc.deleteBook(self.BookId)
        self.mainWindow.loadBookList()

    def editBook(self):
        dialog = DialogUpdateBook(self.BookId, self.BookName, self.BookAuthor, self.BookPrice, self.BookCategory)
        dialog.exec_()
        self.mainWindow.loadBookList()

class DialogUpdateBook(QDialog):
    def __init__(self, BookId, BookName, BookAuthor, BookPrice, BookCategory, filePath=""):
        super().__init__()

        self.BookId = BookId
        self.filePath = filePath
        self.setWindowTitle("Update Book")
        self.setFixedSize(400, 350)

        layout = QVBoxLayout()

        self.bookName = QLineEdit()
        self.bookName.setPlaceholderText("Tên tài liệu")
        self.bookName.setText(BookName)
        layout.addWidget(QLabel("Tên tài liệu:"))
        layout.addWidget(self.bookName)

        self.bookAuthor = QLineEdit()
        self.bookAuthor.setPlaceholderText("Đơn vị ban hành")
        self.bookAuthor.setText(BookAuthor)
        layout.addWidget(QLabel("Đơn vị ban hành:"))
        layout.addWidget(self.bookAuthor)

        self.bookPrice = QLineEdit()
        self.bookPrice.setPlaceholderText("Mã tài liệu")
        self.bookPrice.setText(str(BookPrice))  # Chuyển đổi sang chuỗi
        layout.addWidget(QLabel("Mã tài liệu:"))
        layout.addWidget(self.bookPrice)

        self.bookCategory = QComboBox()
        self.bookCategory.addItems(["Loại 1", "Loại 2", "Loại 3"])  # Thêm các loại tài liệu tại đây
        self.bookCategory.setCurrentText(BookCategory)
        layout.addWidget(QLabel("Loại tài liệu:"))
        layout.addWidget(self.bookCategory)

        self.fileLabel = QLabel("Chưa có file được chọn")
        if filePath:
            self.fileLabel.setText(filePath)
        layout.addWidget(self.fileLabel)

        self.browseButton = QPushButton("Browse")
        self.browseButton.clicked.connect(self.browseFile)
        layout.addWidget(self.browseButton)

        self.buttonUpdate = QPushButton(text="Update")
        self.buttonUpdate.setCursor(Qt.PointingHandCursor)
        self.buttonUpdate.clicked.connect(self.updateBook)
        layout.addWidget(self.buttonUpdate)

        self.setLayout(layout)

    def browseFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Select File")
        if filePath:
            self.fileLabel.setText(filePath)
            self.filePath = filePath

    def updateBook(self):
        book_name = self.bookName.text()
        book_author = self.bookAuthor.text()
        book_price = self.bookPrice.text()
        book_category = self.bookCategory.currentText()
        file_path = self.filePath

        if book_name and book_author and book_price and book_category:
            dc.updateBook(self.BookId, book_name, book_author, book_price, book_category, file_path)
            self.accept()