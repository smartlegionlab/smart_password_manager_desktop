# --------------------------------------------------------
# Licensed under the terms of the BSD 3-Clause License
# (see LICENSE for details).
# Copyright © 2018-2024, A.A. Suvorov
# All rights reserved.
# --------------------------------------------------------
# https://github.com/smartlegionlab/
# --------------------------------------------------------
import json
from pathlib import Path

from smartpasslib.generators import SmartPasswordMaster


class SmartPassword:
    """
    Smart password.
    Smart password with the ability to recover and
    linking to a login and a secret phrase.
    The password itself is not stored either in the open or
    in encrypted form, but is generated on the fly.
    """

    def __init__(self, login='', key='', length=12):
        """
        When creating an object, it should be passed:
        :param login: login.
        :param key: a public key that needs to be generated before creating a
        password using a username and a secret phrase.
        :param length: password length.
        """
        self._login = login
        self._length = length
        self._key = key

    @property
    def login(self):
        """Get login"""
        return self._login

    @property
    def key(self):
        """get public key"""
        return self._key

    @property
    def length(self):
        """Get password length"""
        return self._length


class SmartPassMan:
    """
    Password manager.
    Passwords are not stored in clear or encrypted form.
    Passwords are generated on the fly using metadata.
    """
    # The path to the file where the password metadata will be stored.
    file = Path(Path.home()).joinpath('.cases.json')

    def __init__(self):
        self.smart_pass_master = SmartPasswordMaster()
        self._passwords = {}

    @property
    def passwords(self):
        """
        Dictionary with password objects.
        :return: <dict> - dictionary with password objects.
        """
        return self._passwords

    @property
    def count(self):
        """
        Number of passwords.
        :return: <int> - number of passwords.
        """
        return len(self._passwords)

    def add(self, password):
        """
        Adds a password object to the store.
        :param password: SmartPassword object.
        :return: None
        """
        if password not in self._passwords:
            self._passwords[password.login] = password

    def add_smart_pass(self, login, secret, length):
        """
        Creates and saves a new SmartPassword object.
        :param login: login.
        :param secret: secret phrase.
        :param length: password length.
        :return: SmartPassword object.
        """
        key = self.smart_pass_master.generate_public_key(login=login, secret=secret)
        smart_password = SmartPassword(login=login, key=key, length=length)
        self.add(smart_password)
        return smart_password

    def add_passwords(self, passwords):
        """
        Adds passwords to the store.
        :param passwords: an iterable with password objects.
        :return: None
        """
        for password in passwords:
            if isinstance(password, SmartPassword):
                self.add(password)

    def get_password(self, login):
        """
        Looks for a password object in the store by login.
        :param login: login.
        :return: Returns a SmartPassword object.
        """
        return self._passwords.get(login)

    def remove(self, login: str) -> None:
        """
        Removes a password object from storage.
        :param login: login.
        :return: None
        """
        if login in self._passwords:
            del self._passwords[login]

    def load_file(self):
        """Loads password objects from a file."""
        try:
            with open(self.file, 'r') as f:
                json_data = json.load(f)
        except json.decoder.JSONDecodeError:
            return {}
        except FileNotFoundError:
            self.file = Path(Path.home()).joinpath('.cases.json')
            self.save_file()
            return {}
        else:
            passwords = [
                SmartPassword(
                    login=json_data[obj]['login'],
                    key=json_data[obj]['key'],
                    length=json_data[obj]['length']
                ) for obj in json_data]
            self.add_passwords(passwords)
            return passwords

    def save_file(self):
        """Saves password objects to a file."""
        passwords_dict = {name: {'login': password.login,
                                 'length': password.length,
                                 'key': password.key}
                          for name, password in self._passwords.items()}
        self._save_file(passwords_dict)

    def clear(self):
        """Cleans up storage."""
        self._passwords = {}

    def _save_file(self, passwords: dict):
        """Writes json data to a file."""
        with open(self.file, 'w') as f:
            json.dump(passwords, f, indent=4)
