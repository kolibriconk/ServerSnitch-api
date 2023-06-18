import mysql.connector
from enum import IntEnum


class DatabaseContext:
    _instance = None

    class DataType(IntEnum):
        BOOL = 1
        INT = 2
        FLOAT = 3
        STRING = 4

    class ActionType(IntEnum):
        START = 1
        REBOOT = 2

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.cnx = mysql.connector.connect(user="monitor", password="bJ3@RnXi*m",
                                                        host="localhost", database="server_snitch")
        return cls._instance

    def __del__(self):
        self.cnx.close()

    def get_cursor(self):
        return self.cnx.cursor(buffered=True)

    # API methods

    def store_value(self, name, value, type, device_id):
        cursor = self.get_cursor()
        cursor.execute("INSERT INTO DataValue (Id, Name, Value, Type, DeviceId) "
                       "VALUES (NULL, %s, %s, %s, %s)", (name, value, int(type), device_id))
        self.cnx.commit()
        cursor.close()

    def is_device_registered(self, device_id):
        cursor = self.get_cursor()
        cursor.execute("SELECT EUI FROM Device WHERE EUI = %s", (device_id,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None

    # Web methods

    def get_user(self, username, password_hash):
        # get the user if the hash matches and the user too
        cursor = self.get_cursor()
        cursor.execute("SELECT Id FROM User WHERE User = %s AND PwdHash = %s", (username, password_hash))
        result = cursor.fetchone()
        cursor.close()

        if result is None:
            return None
        else:
            return result[0]

    def check_user(self, username):
        # return true if the user exists
        cursor = self.get_cursor()
        cursor.execute("SELECT Id FROM User WHERE User = %s", (username,))
        result = cursor.fetchone()
        cursor.close()

        if result is None:
            return False
        else:
            return True

    def create_user(self, name, username, password_hash):
        try:
            cursor = self.get_cursor()
            cursor.execute("INSERT INTO User (Id, Name, User, PwdHash) VALUES (NULL, %s, %s, %s)", (name, username, password_hash))
            self.cnx.commit()
            cursor.close()

            cursor = self.get_cursor()
            cursor.execute("SELECT Id FROM User WHERE User = %s AND PwdHash = %s", (username, password_hash))
            result = cursor.fetchone()
            cursor.close()
        except:
            return False

        if result is None:
            return False
        else:
            return True

    def create_group(self, name, description, user_id):
        try:
            cursor = self.get_cursor()
            cursor.execute("INSERT INTO DeviceGroup (Id, Alias, Description) VALUES (NULL, %s, %s)", (name, description))
            group_id = cursor.lastrowid
            cursor.execute("INSERT INTO UserDeviceGroup (UserId, DeviceGropuId) VALUES (%s, %s)", (user_id, group_id))
            self.cnx.commit()
            cursor.close()

            cursor = self.get_cursor()
            cursor.execute("SELECT Id FROM DeviceGroup WHERE Id = %s", (group_id,))
            result = cursor.fetchone()
            cursor.close()
        except:
            return False

        if result is None:
            return False
        else:
            return True

    def get_groups(self, user_id):
        cursor = self.get_cursor()
        cursor.execute("SELECT Id, Alias, Description FROM UserDeviceGroup udg INNER JOIN DeviceGroup dg ON "
                          "udg.DeviceGropuId = dg.Id WHERE udg.UserId = %s", (user_id,))

        result = cursor.fetchall()
        cursor.close()

        if result is None:
            return None
        else:
            return result

    def get_devices(self, group_id):
        cursor = self.get_cursor()
        cursor.execute("SELECT EUI, Alias, Description FROM Device WHERE GroupId = %s", (group_id,))

        result = cursor.fetchall()
        cursor.close()

        if result is None:
            return None
        else:
            return result

    def create_device(self, eui, mac, name, description, group_id, user_id):
        try:
            cursor = self.get_cursor()
            cursor.execute("INSERT INTO Device (EUI, MAC, Alias, Description, GroupId, UserId) VALUES (%s, %s, %s, %s, %s, %s)", (eui, mac, name, description, group_id, user_id))
            self.cnx.commit()
            cursor.close()

            cursor = self.get_cursor()
            cursor.execute("SELECT EUI FROM Device WHERE EUI = %s", (eui,))
            result = cursor.fetchone()
            cursor.close()
        except:
            return False

        if result is None:
            return False
        else:
            return True

    def get_device_status(self, device_id):
        cursor = self.get_cursor()
        cursor.execute("SELECT DISTINCT(Name), `TimeStamp`, `Value` FROM DataValue WHERE DeviceId = %s "
                       "AND Name = 'system.status' ORDER BY `TimeStamp` DESC", (device_id,))

        result = cursor.fetchone()
        cursor.close()

        if result is None:
            return None
        else:
            return result

    def get_services(self, device_id):
        cursor = self.get_cursor()
        cursor.execute("SELECT DISTINCT(Name) FROM DataValue WHERE DeviceId = %s "
                       "AND NOT(Name = 'system.wan' or Name = 'system.lan' or Name like '%.status')", (device_id,))

        result = cursor.fetchall()
        cursor.close()

        if result is None:
            return None
        else:
            return result

    def get_statuses(self, device_id):
        cursor = self.get_cursor()
        cursor.execute("SELECT DISTINCT(Name), `TimeStamp`, `Value` FROM DataValue WHERE DeviceId = %s "
                       "AND (Name = 'system.wan' or Name = 'system.lan' or Name like '%.status')"
                       "ORDER BY `TimeStamp` DESC", (device_id,))

        result = cursor.fetchall()
        cursor.close()

        if result is None:
            return None
        else:
            return result

    def get_data(self, service_name, device_id):
        cursor = self.get_cursor()
        cursor.execute("SELECT Name, Value, Timestamp, Type FROM DataValue WHERE Name = %s AND DeviceId = %s", (service_name, device_id))

        result = cursor.fetchall()
        cursor.close()

        if result is None:
            return None
        else:
            return result

    def get_device(self, device_id):
        cursor = self.get_cursor()
        cursor.execute("SELECT EUI FROM Device WHERE EUI = %s", (device_id,))

        result = cursor.fetchone()
        cursor.close()

        if result is None:
            return None
        else:
            return result[0]

    def log_action(self, device_id, action):
        # Get user id from device
        cursor = self.get_cursor()
        cursor.execute("SELECT UserId FROM Device WHERE EUI = %s", (device_id,))
        result = cursor.fetchone()
        cursor.close()

        if result is None:
            return False
        else:
            user_id = result[0]
            cursor = self.get_cursor()
            cursor.execute("INSERT INTO ActionLog (UserId, DeviceId, Action) VALUES (%s, %s, %s)", (user_id, device_id, action))
            self.cnx.commit()
            cursor.close()
            return True
