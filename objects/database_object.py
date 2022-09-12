import sqlite3


class ShippingCodesDB:
    def __init__(self):
        self.__cursor = None
        self.__conn = None

    def connect(self, name):
        self.__conn = sqlite3.connect(name, timeout=10)
        self.__cursor = self.__conn.cursor()

    def init_database(self):
        self.__cursor.execute("CREATE TABLE codes (package_owner text, delivery_code text, courier_code text, name text, last_update text, last_update_courier text)")

    def add_shipping_code(self, package_owner, delivery_code, courier_code, name, last_update, last_update_courier):
        self.__cursor.execute("INSERT INTO {tn} (package_owner, delivery_code, courier_code, name, last_update, last_update_courier) VALUES (?, ?, ?, ?, ?, ?)".format(tn="codes"),
                              (str(package_owner), str(delivery_code), str(courier_code),
                               str(name), str(last_update), str(last_update_courier)))

    def remove_shipping_code(self, name):
        self.__cursor.execute('''DELETE FROM codes WHERE name = ?''', (name,))

    def tracking_stop(self, code, carrier):
        self.__cursor.execute('''DELETE FROM codes WHERE delivery_code = ? AND courier_code = ?''', (code, carrier,))

    def has_been_updated(self, name, timestamp):
        self.__cursor.execute('''SELECT last_update FROM codes WHERE name = ?''', (name,))
        last_update = self.__cursor.fetchone()
        
        if last_update[0] is not timestamp:
            return True
        return False

    def has_courier_updated(self, name, timestamp):
        self.__cursor.execute('''SELECT last_courier_update FROM codes WHERE name = ?''', (name,))
        last_update = self.__cursor.fetchone()

        if last_update[0] is not timestamp:
            return True
        return False

    def get_name(self, code, carrier):
        self.__cursor.execute('''SELECT name FROM codes WHERE delivery_code = (?) AND courier_code = (?)''', [str(code), str(carrier)])
        name = self.__cursor.fetchone()
        if name is not None:
            name = name[0]

        return name

    def get_code(self, name, user):
        self.__cursor.execute('''SELECT delivery_code FROM codes WHERE name = (?) AND package_owner = (?)''', [str(name), str(user)])
        delivery_code = self.__cursor.fetchone()
        if delivery_code is None:
            return -1

        return delivery_code[0]

    def get_all_codes(self, user):
        self.__cursor.execute('''SELECT delivery_code, name FROM codes WHERE package_owner = (?)''', (user,))
        codes = self.__cursor.fetchall()

        return codes

    def get_user(self, code, carrier):
        self.__cursor.execute('''SELECT package_owner FROM codes WHERE delivery_code = (?) AND courier_code = (?) ''', [str(code), str(carrier)])
        users = self.__cursor.fetchone()

        return users

    def get_courier_code(self, name):
        self.__cursor.execute('''SELECT courier_code FROM codes WHERE name = ?''', (name,))
        courier_code = self.__cursor.fetchone()
        if courier_code is None:
            return -1

        return courier_code[0]

    def modify_last_update(self, name, last_update):
        self.__cursor.execute('''UPDATE codes SET last_update = ? WHERE name = ?''',
                              [str(last_update), str(name)])

    def modify_last_courier_update(self, name, last_courier_update):
        self.__cursor.execute('''UPDATE codes SET last_update_courier = ? WHERE name = ?''',
                              [str(last_courier_update), str(name)])

    def modify_courier_code(self, name, new_courier):
        self.__cursor.execute('''UPDATE codes SET courier_code = ? WHERE name = ?''',
                              [str(new_courier), str(name)])

    def commit_changes(self):
        self.__conn.commit()

    def close(self):
        self.__conn.close()
