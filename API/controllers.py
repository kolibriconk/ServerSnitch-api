from flask import Flask, request
from Database.database import DatabaseContext

app = Flask(__name__)


@app.route('/monitor/data', methods=['POST'])
def monitor_data():
    data = request.get_json()
    services = data["services"]
    device_id = data["eui"]

    if DatabaseContext().is_device_registered(device_id):
        for service in services.keys():
            print(service)
            name = services[service]["name"]

            for key in ["status", "cpu_percent", "memory_rss"]:
                data_name = f"{name}.{key}"
                type = DatabaseContext.DataType.BOOL if key == "status" else DatabaseContext.DataType.FLOAT
                DatabaseContext().store_value(data_name, services[service][key], type, device_id)

        for key in ["load_avg", "mem", "wan", "lan"]:
            data_name = f"system.{key}"
            if key in ["wan", "lan"]:
                type = DatabaseContext.DataType.BOOL
            else:
                type = DatabaseContext.DataType.FLOAT
            DatabaseContext().store_value(data_name, data[key], type, device_id)

        DatabaseContext().store_value("system.status", "True", DatabaseContext.DataType.BOOL, device_id)
        return "Success", 200
    else:
        return "Device not registered", 400


@app.route('/pybytes/integration', methods=['POST'])
def pybytes_integration():
    """This message enters with a byte array
    The first part is the EUI of the device
    The second part has the lan status of the server
    And the last part has the wan status of the server"""
    print("Entered pybytes_integration")
    data = request.get_json()

    if "pcup!" in data:
        if len(data) == len("pcup!0000000000000000"):
            # Get EUI from data and store system.status = True
            device_id = data[5:]
            DatabaseContext().store_value("system.status", "True", DatabaseContext.DataType.BOOL, device_id)
        elif len(data) > len("pcup!0000000000000000"):
            # Get EUI from data, store system.status = True, get lan, wan status and store them
            device_id = data[5:]
            splitted = data.split("!")
            wan = splitted[2]
            lan = splitted[3]
            services = dict(splitted[4])
            DatabaseContext().store_value("system.wan", wan, DatabaseContext.DataType.BOOL, device_id)
            DatabaseContext().store_value("system.lan", lan, DatabaseContext.DataType.BOOL, device_id)
            DatabaseContext().store_value("system.status", "True", DatabaseContext.DataType.BOOL, device_id)

            for service in services.keys():
                name = services[service]["name"]
                data_name = f"{name}.status"
                DatabaseContext().store_value(data_name, service["status"], DatabaseContext.DataType.BOOL, device_id)

    elif "pcdown!" in data and len(data) == len("pcdown!0000000000000000"):
        # Get EUI from data and store system.status = False
        device_id = data[7:]
        DatabaseContext().store_value("system.status", "False", DatabaseContext.DataType.BOOL, device_id)
        DatabaseContext().store_value("system.wan", "False", DatabaseContext.DataType.BOOL, device_id)
        DatabaseContext().store_value("system.lan", "False", DatabaseContext.DataType.BOOL, device_id)

    print(data)

    return "Success", 200


@app.route('/ttn/integration', methods=['POST'])
def ttn_integration():
    """
    This message enters with a byte array
    :return:
    """

    raise NotImplementedError


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)
