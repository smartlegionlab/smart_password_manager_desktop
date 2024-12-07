# --------------------------------------------------------
# Licensed under the terms of the BSD 3-Clause License
# (see LICENSE for details).
# Copyright © 2018-2024, A.A. Suvorov
# All rights reserved.
# --------------------------------------------------------
# https://github.com/smartlegionlab/
# --------------------------------------------------------
import webbrowser

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QLineEdit,
    QDialog,
    QTableWidget,
    QTableWidgetItem,
    QSpinBox,
    QFrame,
    QHeaderView
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from core.config import Config
from core.model import SmartPasswordFactory
from core.manager import SmartPasswordManager


class PasswordInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Enter the data to create a smart password:')

        self.layout = QVBoxLayout(self)

        self.login_label = QLabel('Login:')
        self.layout.addWidget(self.login_label)
        self.login_input = QLineEdit(self)
        self.layout.addWidget(self.login_input)

        self.secret_label = QLabel('Secret Phrase:')
        self.layout.addWidget(self.secret_label)
        self.secret_input = QLineEdit(self)
        self.secret_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.secret_input)

        self.length_label = QLabel('Password Length:')
        self.layout.addWidget(self.length_label)
        self.length_input = QSpinBox(self)
        self.length_input.setMinimum(4)
        self.length_input.setMaximum(1000)
        self.length_input.setValue(15)
        self.layout.addWidget(self.length_input)

        self.submit_button = QPushButton('Create a password', self)
        self.submit_button.clicked.connect(self.accept)
        self.layout.addWidget(self.submit_button)

    def get_inputs(self):
        return self.login_input.text(), self.secret_input.text(), self.length_input.value()


class SecretInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Enter the secret phrase')

        self.layout = QVBoxLayout(self)

        self.secret_label = QLabel('Secret Phrase:')
        self.layout.addWidget(self.secret_label)
        self.secret_input = QLineEdit(self)
        self.secret_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.secret_input)

        self.submit_button = QPushButton('Confirm', self)
        self.submit_button.clicked.connect(self.accept)
        self.layout.addWidget(self.submit_button)

    def get_secret(self):
        return self.secret_input.text()


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = Config()
        self.smart_pass_man = SmartPasswordManager()
        self.setWindowTitle(f'{self.config.description}')
        self.resize(800, 600)

        self.vertical_layout = QVBoxLayout()
        self.label_logo = QLabel()
        font = QFont()
        font.setPointSize(24)
        self.label_logo.setFont(font)
        self.label_logo.setAlignment(Qt.AlignCenter)
        self.label_logo.setText(f"{self.config.title} <sup>SL</sup>")
        self.vertical_layout.addWidget(self.label_logo)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(['Login', 'Length', 'Public Key', 'Get', 'Delete'])
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)

        for i in range(5):
            self.table_widget.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)

        self.vertical_layout.addWidget(self.table_widget)

        self.btn_new_password = QPushButton(self.config.btn_new_pass_title)
        self.btn_new_password.clicked.connect(self.add_password)
        self.vertical_layout.addWidget(self.btn_new_password)

        self.btn_help = QPushButton(self.config.btn_help_title)
        self.btn_help.clicked.connect(lambda: webbrowser.open(self.config.url))
        self.vertical_layout.addWidget(self.btn_help)

        self.btn_exit = QPushButton(self.config.btn_exit_title)
        self.btn_exit.clicked.connect(self.close)
        self.vertical_layout.addWidget(self.btn_exit)

        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.vertical_layout.addWidget(self.line)

        self.copyright_label = QLabel()
        self.copyright_label.setAlignment(Qt.AlignCenter)
        self.copyright_label.setText(self.config.copyright)
        self.vertical_layout.addWidget(self.copyright_label)

        self.setLayout(self.vertical_layout)
        self._init()

    def _init(self):
        self.table_widget.setRowCount(0)
        for password in self.smart_pass_man.smart_passwords.values():
            self.add_item(password)

    def add_item(self, smart_password):
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)

        self.table_widget.setItem(row_position, 0, QTableWidgetItem(smart_password.login))

        self.table_widget.setItem(row_position, 1, QTableWidgetItem(str(smart_password.length)))

        public_key_display = f"{smart_password.key[:4]}****{smart_password.key[-4:]}"
        self.table_widget.setItem(row_position, 2, QTableWidgetItem(public_key_display))

        get_button = QPushButton("Get")
        get_button.clicked.connect(lambda: self.get_password(smart_password.login))
        self.table_widget.setCellWidget(row_position, 3, get_button)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.remove_password(smart_password.login))
        self.table_widget.setCellWidget(row_position, 4, delete_button)

    def remove_password(self, login):
        row = self.find_row_by_login(login)
        if row != -1:
            status = self.question('Remove password', 'Do you want to continue?\n')
            if status:
                self.table_widget.removeRow(row)
                self.smart_pass_man.delete_smart_password(login)

    def find_row_by_login(self, login):
        for row in range(self.table_widget.rowCount()):
            if self.table_widget.item(row, 0).text() == login:
                return row
        return -1

    def add_password(self):
        dialog = PasswordInputDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            login, secret, length = dialog.get_inputs()

            if login in self.smart_pass_man.smart_passwords:
                self.show_msg('Error!', 'Login already exists! Please choose another login.')
                return

            if login and secret:
                key = self.smart_pass_man.generate_public_key(login=login, secret=secret)
                smart_password = SmartPasswordFactory.create_smart_password(login=login, key=key, length=length)
                password = self.smart_pass_man.generate_smart_password(
                    login=smart_password.login,
                    secret=secret,
                    length=length,
                )
                self.smart_pass_man.add_smart_password(smart_password)
                self.add_item(smart_password)
                self.show_dialog('Information:', "Your password: ", text=f'{password}')
            else:
                msg = 'Unable to create a password! '
                if not login:
                    msg += 'Login not received! '

                if not secret:
                    msg += 'Secret phrase not received!'
                self.show_msg('Attention!', f'{msg}')

    def get_password(self, login):
        row = self.find_row_by_login(login)
        if row != -1:
            dialog = SecretInputDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                secret = dialog.get_secret()
                if secret:
                    smart_password = self.smart_pass_man.get_smart_password(login)
                    check_status = self.smart_pass_man.check_public_key(
                        login=smart_password.login,
                        secret=secret,
                        public_key=smart_password.key
                    )
                    if check_status:
                        password = self.smart_pass_man.generate_smart_password(
                            smart_password.login,
                            secret,
                            smart_password.length
                        )
                        self.show_dialog('Information', "Your password: ", text=f'{password}')
                    else:
                        self.show_msg(
                            'Attention!',
                            'Incorrect secret phrase! Perhaps '
                            'Caps lock, a different language, '
                            'or keyboard layout is enabled.'
                        )
                else:
                    self.show_msg('Attention!', 'Please enter the secret phrase!')
        else:
            self.show_msg('Attention!', 'Choose a password!')

    def question(self, title, msg):
        args = (self, title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        reply = QMessageBox.question(*args)
        return reply == QMessageBox.Yes

    def show_dialog(self, title, name, text):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)

        layout = QVBoxLayout(dialog)

        label = QLabel(name)
        layout.addWidget(label)

        password_text = QLineEdit()
        password_text.setText(text)
        password_text.setReadOnly(True)
        layout.addWidget(password_text)

        copy_button = QPushButton("Copy to clipboard")
        copy_button.clicked.connect(lambda: self.copy_to_clipboard(password_text.text(), dialog))
        layout.addWidget(copy_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def copy_to_clipboard(self, text, dialog):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.show_msg('Success!', 'Password copied to clipboard.')
        dialog.accept()

    def show_msg(self, title, msg):
        QMessageBox.about(self, title, msg)

    def closeEvent(self, event) -> None:
        reply = QMessageBox.question(
            self,
            'Exit',
            'Do you want to continue?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.hide()
            event.accept()
        else:
            event.ignore()


def main():
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
