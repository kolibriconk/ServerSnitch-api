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
        return self.cnx.cursor()

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
