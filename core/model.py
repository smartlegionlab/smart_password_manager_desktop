# --------------------------------------------------------
# Licensed under the terms of the BSD 3-Clause License
# (see LICENSE for details).
# Copyright © 2018-2024, A.A. Suvorov
# All rights reserved.
# --------------------------------------------------------
# https://github.com/smartlegionlab/
# --------------------------------------------------------


class SmartPassword:
    def __init__(self, login: str, key: str, length=12):
        self._login = login
        self._length = length
        self._key = key

    @property
    def login(self):
        return self._login

    @property
    def key(self):
        return self._key

    @property
    def length(self):
        return self._length

    def to_dict(self):
        return {
            "login": self._login,
            "key": self._key,
            "length": self._length
        }

    @staticmethod
    def from_dict(data):
        return SmartPassword(login=data['login'], key=data['key'], length=data['length'])


class SmartPasswordFactory:

    @classmethod
    def create_smart_password(cls, login, key, length):
        return SmartPassword(login=login, key=key, length=length)
