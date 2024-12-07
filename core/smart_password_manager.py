# --------------------------------------------------------
# Licensed under the terms of the BSD 3-Clause License
# (see LICENSE for details).
# Copyright © 2018-2024, A.A. Suvorov
# All rights reserved.
# --------------------------------------------------------
# https://github.com/smartlegionlab/
# --------------------------------------------------------
import os
import json

from smartpasslib import SmartPasswordMaster

from core.smart_password_factory import SmartPassword


class SmartPasswordManager:
    def __init__(self, filename='~/.cases.json'):
        self.filename = os.path.expanduser(filename)
        self.smart_passwords = self._load_data()

    @staticmethod
    def generate_base_password(length=10):
        return SmartPasswordMaster.generate_strong_password(length)

    @classmethod
    def generate_default_smart_password(cls, secret='', length=10):
        return SmartPasswordMaster.generate_default_smart_password(secret, length)

    @classmethod
    def generate_smart_password(cls, login='', secret='', length=10):
        return SmartPasswordMaster.generate_smart_password(login, secret, length)

    @classmethod
    def generate_public_key(cls, login, secret):
        return SmartPasswordMaster.generate_public_key(login, secret)

    @classmethod
    def check_public_key(cls, login, secret, public_key):
        return SmartPasswordMaster.check_public_key(login, secret, public_key)

    def add_smart_password(self, smart_password: SmartPassword):
        self.smart_passwords[smart_password.login] = smart_password
        self._write_data()

    def get_smart_password(self, login: str):
        return self.smart_passwords.get(login)

    def delete_smart_password(self, login: str):
        if login in self.smart_passwords:
            del self.smart_passwords[login]
            self._write_data()
        else:
            raise KeyError("Login not found.")

    def _load_data(self):
        print(self.filename)
        if os.path.isfile(self.filename):
            with open(self.filename, 'r') as f:
                data = json.load(f)
                return {login: SmartPassword.from_dict(item) for login, item in data.items()}
        else:
            return {}

    def load_data(self):
        self._load_data()

    def save_data(self):
        self._write_data()

    def _ensure_file_exists(self):
        if not os.path.isfile(self.filename):
            with open(self.filename, 'w') as f:
                json.dump({}, f)

    def _write_data(self):
        with open(self.filename, 'w') as f:
            json.dump({login: sp.to_dict() for login, sp in self.smart_passwords.items()}, f, indent=4)
