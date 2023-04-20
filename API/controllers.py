from flask import Flask, request
from database import DatabaseContext

app = Flask(__name__)


@app.route('/monitor/data', methods=['POST'])
def monitor_data():
    data = request.get_json()
    services = data['services']
    device_id = data["eui"]

    for service in services.items():
        print(service)
        name = service["name"]
        for key in ["cpu_percent", "memory_rss"]:
            data_name = f"{name}.{service[key]}"
            type = DatabaseContext.DataType.FLOAT
            DatabaseContext().store_value(data_name, service[key], type, device_id)

    for key in ["load_avg", "memory"]:
        data_name = f"system.{data[key]}"
        type = DatabaseContext.DataType.FLOAT
        DatabaseContext().store_value(data_name, data[key], type, device_id)

    return "Success"


if __name__ == '__main__':
    app.run()
