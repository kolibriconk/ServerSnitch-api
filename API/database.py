import mysql.connector
from enum import Enum


class DatabaseContext:
    _instance = None

    class DataType(Enum):
        BOOL = 0
        INT = 1
        FLOAT = 2
        STRING = 3

    class ActionType(Enum):
        START = 0
        REBOOT = 1

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.cnx = mysql.connector.connect(user='root', password='FI!!612Y0s',
                                                        host='192.168.1.100', database='server_snitch')
        return cls._instance

    def __del__(self):
        self.cnx.close()

    def get_cursor(self):
        return self.cnx.cursor()

    def store_value(self, name, value, type, device_id):
        cursor = self.get_cursor()
        cursor.execute("INSERT INTO DataValue (Id, Name, Value, Type, DeviceId) "
                       "VALUES (NULL, %s, %s, %d, %s)", (name, value, type, device_id))
        self.cnx.commit()
        cursor.close()

