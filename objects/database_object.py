import sqlite3


class DiscordUsers:
    def __init__(self):
        self.__cursor = None
        self.__conn = None

    def connect(self, name):
        self.__conn = sqlite3.connect(name, timeout=10)
        self.__cursor = self.__conn.cursor()

    def init_database(self):
        #   0 is false
        #   1 is true
        self.__cursor.execute("CREATE TABLE users (discord_user text, has_agreed integer)")

    def add_user(self, user):
        self.__cursor.execute("INSERT INTO users (discord_user, has_agreed) VALUES (?, ?)", (str(user), 1,))

    def remove_user(self, user):
        self.__cursor.execute("DELETE FROM users WHERE discord_user = ?", (str(user),))

    def check_user(self, user):
        self.__cursor.execute("SELECT * FROM users WHERE discord_user = ?", (str(user),))
        user_in_db = self.__cursor.fetchone()

        if user_in_db is None:
            return False
        else:
            return True

    def commit_changes(self):
        self.__conn.commit()

    def close(self):
        self.__conn.close()


class ShippingCodesDB:
    def __init__(self):
        self.__cursor = None
        self.__conn = None

    def connect(self, name):
        self.__conn = sqlite3.connect(name, timeout=10)
        self.__cursor = self.__conn.cursor()

    def init_database(self):
        self.__cursor.execute("CREATE TABLE codes (package_owner text, delivery_code text, carrier_code text, name text, carrier_detect text)")

    def add_shipping_code(self, package_owner, delivery_code, carrier_code, name, carrier_detect):
        self.__cursor.execute("INSERT INTO codes (package_owner, delivery_code, carrier_code, name, carrier_detect) VALUES (?, ?, ?, ?, ?)",
                              (str(package_owner), str(delivery_code), str(carrier_code),
                               str(name), str(carrier_detect)))

    def remove_shipping_code(self, user_id, name):
        self.__cursor.execute('''DELETE FROM codes WHERE name = ? AND package_owner = ?''', (name, str(user_id)))

    def tracking_stop(self, code, carrier):
        self.__cursor.execute('''DELETE FROM codes WHERE delivery_code = ? AND carrier_code = ?''', (code, carrier,))

    def get_names(self, code, carrier):
        self.__cursor.execute('''SELECT name FROM codes WHERE delivery_code = (?) AND carrier_code = (?)''', [str(code), str(carrier)])
        name = self.__cursor.fetchall()
        print
        return name

    def get_users(self, code, carrier):
        self.__cursor.execute('''SELECT package_owner FROM codes WHERE delivery_code = (?) AND carrier_code = (?) ''', [str(code), str(carrier)])
        users = self.__cursor.fetchall()

        return users

    def get_carrier_code(self, user_id, name):
        self.__cursor.execute('''SELECT carrier_code FROM codes WHERE name = ? AND package_owner = ?''', (name, user_id,))
        carrier_code = self.__cursor.fetchone()
        if carrier_code is None:
            return None

        return carrier_code[0]

    def get_code(self, name, user):
        self.__cursor.execute('''SELECT delivery_code FROM codes WHERE name = (?) AND package_owner = (?)''', [str(name), str(user)])
        delivery_code = self.__cursor.fetchone()
        if delivery_code is None:
            return -1

        return delivery_code[0]

    def get_all_codes(self, user):
        self.__cursor.execute('''SELECT name FROM codes WHERE package_owner = ?''', (user,))
        codes = self.__cursor.fetchall()

        return codes

    def get_carrier_data(self, tracking_code, carrier_code):
        if carrier_code is None:
            self.__cursor.execute('''SELECT carrier_code FROM codes WHERE delivery_code = ? AND carrier_detect = ?''',
                                  (tracking_code, "automatic"))
        else:
            self.__cursor.execute('''SELECT carrier_code FROM codes WHERE delivery_code = ? AND carrier_code = ?''',
                                  (tracking_code, carrier_code))

        return self.__cursor.fetchone()

    def rename_code(self, name, new_name, user_id):
        self.__cursor.execute("UPDATE codes SET name = ? WHERE name = ? AND package_owner = ?", (name, new_name, str(user_id)))
        if self.get_code(self, new_name) is not None:
            return True
        else:
            return False

    def commit_changes(self):
        self.__conn.commit()

    def close(self):
        self.__conn.close()
