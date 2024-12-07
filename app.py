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
    QHBoxLayout,
    QListWidget,
    QSpinBox,
    QSpacerItem,
    QSizePolicy,
    QFrame, QInputDialog
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from core.config import Config
from core.smart_password_factory import SmartPasswordFactory
from core.smart_password_manager import SmartPasswordManager


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
        self.vertical_layout_2 = QVBoxLayout()
        self.vertical_layout_3 = QVBoxLayout()
        self.vertical_layout_4 = QVBoxLayout()
        self.horizontal_layout = QHBoxLayout()
        self.label_logo = QLabel()
        font = QFont()
        font.setPointSize(24)
        self.label_logo.setFont(font)
        self.label_logo.setTextFormat(Qt.AutoText)
        self.label_logo.setAlignment(Qt.AlignCenter)
        self.label_logo.setText(f"{self.config.title} <sup>SL</sup>")
        self.vertical_layout_2.addWidget(self.label_logo)
        self.list_widget = QListWidget()
        font = QFont()
        font.setFamily("Noto Sans")
        font.setPointSize(16)
        self.list_widget.setFont(font)
        self.vertical_layout_3.addWidget(self.list_widget)
        self.label_len = QLabel()
        self.label_len.setText(self.config.label_len_title)
        self.horizontal_layout.addWidget(self.label_len)
        self.spin_box = QSpinBox()
        self.spin_box.setMinimum(4)
        self.spin_box.setMaximum(1000)
        self.spin_box.setValue(15)
        self.horizontal_layout.addWidget(self.spin_box)
        self.btn_new_password = QPushButton()
        self.btn_new_password.setText(self.config.btn_new_pass_title)
        self.horizontal_layout.addWidget(self.btn_new_password)
        self.btn_remove_pass = QPushButton()
        self.btn_remove_pass.setText(self.config.btn_remove_pass_title)
        self.horizontal_layout.addWidget(self.btn_remove_pass)
        spacer_item = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontal_layout.addItem(spacer_item)
        self.btn_get_password = QPushButton()
        self.btn_get_password.setText(self.config.btn_get_password_title)
        self.horizontal_layout.addWidget(self.btn_get_password)
        self.btn_help = QPushButton()
        self.btn_help.setText(self.config.btn_help_title)
        self.horizontal_layout.addWidget(self.btn_help)
        self.btn_exit = QPushButton()
        self.btn_exit.setText(self.config.btn_exit_title)
        self.horizontal_layout.addWidget(self.btn_exit)
        self.vertical_layout_4.addLayout(self.horizontal_layout)
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.vertical_layout_4.addWidget(self.line)
        self.copyright_label = QLabel()
        self.copyright_label.setAlignment(Qt.AlignCenter)
        self.copyright_label.setText(self.config.copyright)
        self.vertical_layout_4.addWidget(self.copyright_label)
        self.vertical_layout.addLayout(self.vertical_layout_2)
        self.vertical_layout.addLayout(self.vertical_layout_3)
        self.vertical_layout.addLayout(self.vertical_layout_4)
        self.setLayout(self.vertical_layout)
        self.btn_exit.clicked.connect(self.close)
        self.btn_new_password.clicked.connect(self.add_password)
        self.btn_remove_pass.clicked.connect(self.remove_password)
        self.btn_get_password.clicked.connect(self.get_password)
        self.btn_help.clicked.connect(lambda: webbrowser.open(self.config.url))
        self._init()

    def _init(self):
        for password in self.smart_pass_man.smart_passwords.values():
            self.add_item(password.login)

    def add_item(self, password):
        self.list_widget.insertItem(self.list_widget.count() + 1, password)

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

    def add_password(self):
        dialog = PasswordInputDialog(self)
        while True:
            if dialog.exec_() == QDialog.Accepted:
                login, secret, length = dialog.get_inputs()

                if login in self.smart_pass_man.smart_passwords:
                    self.show_msg('Error!', 'Login already exists! Please choose another login.')
                    dialog.login_input.clear()
                    continue

                if login and secret:
                    key = self.smart_pass_man.generate_public_key(login=login, secret=secret)
                    smart_password = SmartPasswordFactory.create_smart_password(login=login, key=key, length=length)
                    password = self.smart_pass_man.generate_smart_password(
                        login=smart_password.login,
                        secret=secret,
                        length=length,
                    )
                    self.smart_pass_man.add_smart_password(smart_password)
                    self.add_item(smart_password.login)
                    self.show_dialog('Information:', "Your password: ", text=f'{password}')
                    break
                else:
                    msg = 'Unable to create a password! '
                    if not login:
                        msg += 'Login not received! '

                    if not secret:
                        msg += 'Secret phrase not received!'
                    self.show_msg('Attention!', f'{msg}')
            else:
                break

    def remove_password(self):
        item = self.list_widget.currentItem()
        if item:
            status = self.question('Remove password', 'Do you want to continue?\n')
            if status:
                self.list_widget.takeItem(self.list_widget.currentRow())
                self.smart_pass_man.delete_smart_password(item.text())

    def question(self, title, msg):
        args = (self, title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        reply = QMessageBox.question(*args)
        if reply == QMessageBox.Yes:
            return True
        return False

    def show_dialog(self, title, name, text):
        QInputDialog.getMultiLineText(self, title, name, text=text)

    def get_password(self):
        item = self.list_widget.currentItem()
        if item:
            dialog = SecretInputDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                secret = dialog.get_secret()
                if secret:
                    smart_password = self.smart_pass_man.get_smart_password(item.text())
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
                        # self.clip.setText(password)
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

    def show_msg(self, title, msg):
        QMessageBox.about(self, title, msg)


def main():
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
