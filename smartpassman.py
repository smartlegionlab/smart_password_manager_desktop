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
    QInputDialog,
    QHBoxLayout,
    QListWidget,
    QSpinBox,
    QSpacerItem,
    QSizePolicy,
    QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from smartpassman.config import Config
from smartpassman.passman import SmartPassMan, SmartPassword


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._config = Config()
        self._smart_pass_man = SmartPassMan()
        self.setWindowTitle(f'{self._config.description}.')
        self.resize(640, 480)
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
        self.label_logo.setText(f"{self._config.title} <sup>SL</sup>")
        self.vertical_layout_2.addWidget(self.label_logo)
        self.list_widget = QListWidget()
        font = QFont()
        font.setFamily("Noto Sans")
        font.setPointSize(16)
        self.list_widget.setFont(font)
        self.vertical_layout_3.addWidget(self.list_widget)
        self.label_len = QLabel()
        self.label_len.setText(self._config.label_len_title)
        self.horizontal_layout.addWidget(self.label_len)
        self.spin_box = QSpinBox()
        self.spin_box.setMinimum(4)
        self.spin_box.setMaximum(1000)
        self.spin_box.setValue(15)
        self.horizontal_layout.addWidget(self.spin_box)
        self.btn_new_password = QPushButton()
        self.btn_new_password.setText(self._config.btn_new_pass_title)
        self.horizontal_layout.addWidget(self.btn_new_password)
        self.btn_remove_pass = QPushButton()
        self.btn_remove_pass.setText(self._config.btn_remove_pass_title)
        self.horizontal_layout.addWidget(self.btn_remove_pass)
        spacer_item = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontal_layout.addItem(spacer_item)
        self.btn_get_password = QPushButton()
        self.btn_get_password.setText(self._config.btn_get_password_title)
        self.horizontal_layout.addWidget(self.btn_get_password)
        self.btn_help = QPushButton()
        self.btn_help.setText(self._config.btn_help_title)
        self.horizontal_layout.addWidget(self.btn_help)
        self.btn_exit = QPushButton()
        self.btn_exit.setText(self._config.btn_exit_title)
        self.horizontal_layout.addWidget(self.btn_exit)
        self.vertical_layout_4.addLayout(self.horizontal_layout)
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.vertical_layout_4.addWidget(self.line)
        self.copyright_label = QLabel()
        self.copyright_label.setAlignment(Qt.AlignCenter)
        self.copyright_label.setText(self._config.copyright)
        self.vertical_layout_4.addWidget(self.copyright_label)
        self.vertical_layout.addLayout(self.vertical_layout_2)
        self.vertical_layout.addLayout(self.vertical_layout_3)
        self.vertical_layout.addLayout(self.vertical_layout_4)
        self.setLayout(self.vertical_layout)
        self.btn_exit.clicked.connect(self.close)
        self.btn_new_password.clicked.connect(self._add_password)
        self.btn_remove_pass.clicked.connect(self._remove_password)
        self.btn_get_password.clicked.connect(self._get_password)
        self.btn_help.clicked.connect(lambda: webbrowser.open(self._config.url))
        self._load_file()

    def _load_file(self):
        self._smart_pass_man.load_file()
        for password in self._smart_pass_man.passwords.values():
            self._add_item(password.login)

    def _save_file(self):
        self._smart_pass_man.save_file()

    def _add_item(self, password):
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
            self._save_file()
            event.accept()
        else:
            event.ignore()

    def _add_password(self):
        login, status_login = QInputDialog.getText(
            self, 'Auth', 'Login:',
            echo=QLineEdit.Normal
        )
        secret, status_secret = QInputDialog.getText(
            self,
            'Getting access',
            "To get the password, enter the secret phrase: ",
            echo=QLineEdit.Password
        )
        length = self.spin_box.value()

        if login and secret and status_login and status_secret:
            key = self._smart_pass_man.smart_pass_master.get_public_key(login=login, secret=secret)
            smart_password = SmartPassword(login=login, key=key, length=length)
            password = self._smart_pass_man.smart_pass_master.get_smart_password(
                login=smart_password.login,
                secret=secret,
                length=length,
            )
            # self.clip.setText(password)
            self._smart_pass_man.add(smart_password)
            self._save_file()
            self._add_item(smart_password.login)
            self._show_dialog('Information:', "Your password: ", text=f'{password}')
        else:
            msg = 'Unable to create a password! '
            if not login:
                msg += 'Login not received! '

            if not secret:
                msg += 'Secret phrase not received!'
            self._show_msg('Attention!', f'{msg}')

    def _remove_password(self):
        item = self.list_widget.currentItem()
        if item:
            status = self._question('Remove password', 'Do you want to continue?\n')
            if status:
                self.list_widget.takeItem(self.list_widget.currentRow())
                self._smart_pass_man.remove(item.text())
                self._save_file()

    def _question(self, title, msg):
        args = (self, title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        reply = QMessageBox.question(*args)
        if reply == QMessageBox.Yes:
            return True
        return False

    def _show_dialog(self, title, name, text):
        QInputDialog.getMultiLineText(self, title, name, text=text)

    def _get_password(self):
        item = self.list_widget.currentItem()
        if item:
            secret, status = QInputDialog.getText(
                self,
                'Getting access',
                "To get the password, enter the secret phrase: ",
                echo=QLineEdit.Password
            )
            if secret and status:
                smart_password = self._smart_pass_man.get_password(item.text())
                check_status = self._smart_pass_man.smart_pass_master.check_data(
                    login=smart_password.login,
                    secret=secret,
                    public_key=smart_password.key
                )
                if check_status:
                    password = self._smart_pass_man.smart_pass_master.get_smart_password(
                        smart_password.login,
                        secret,
                        smart_password.length
                    )
                    # self.clip.setText(password)
                    QInputDialog.getMultiLineText(
                        self,
                        'Information',
                        "Your password: ",
                        text=f'{password}'
                    )
                else:
                    self._show_msg(
                        'Attention!',
                        'Incorrect secret phrase! Perhaps '
                        'Caps lock, a different language, '
                        'or keyboard layout is enabled.'
                    )
            else:
                self._show_msg('Attention!', 'Please enter all the necessary data!')
        else:
            self._show_msg('Attention!', 'Choose a password!')

    def _show_msg(self, title, msg):
        QMessageBox.about(self, title, msg)


def main():
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
