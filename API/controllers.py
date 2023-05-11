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
            for key in ["cpu_percent", "memory_rss"]:
                data_name = f"{name}.{key}"
                type = DatabaseContext.DataType.FLOAT
                DatabaseContext().store_value(data_name, services[service][key], type, device_id)

        for key in ["load_avg", "mem"]:
            data_name = f"system.{key}"
            type = DatabaseContext.DataType.FLOAT
            DatabaseContext().store_value(data_name, data[key], type, device_id)

        return "Success", 200
    else:
        return "Device not registered", 400


if __name__ == '__main__':
    app.run()
