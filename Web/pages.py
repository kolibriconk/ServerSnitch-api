from datetime import datetime

from flask import Flask, render_template, request, jsonify
from paho.mqtt import publish

from Database.database import DatabaseContext

app = Flask(__name__)

API_KEY = "NNSXS.NGQSNYVXSKXZGFCMGNBPYEUQVE7QBUQR3UEZZUA.XEM5I3EQVKL6B7I3BVY33NKO3HCBK4NEMJQVKSVVEV7RPPGFYAFA"
HOSTNAME = "eu1.cloud.thethings.network"
USERNAME = "server-snitch@ttn"
AUTH = {'username': USERNAME, 'password': API_KEY}


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/register')
def register():
    return render_template("register.html")


@app.route('/login', methods=['POST'])
def login_post():
    data = request.get_json()
    username = data['username']
    password = data['password']
    id = DatabaseContext().get_user(username, password)
    if id is None:
        return 'Invalid username or password', 401
    else:
        return jsonify(id), 200


@app.route('/register', methods=['POST'])
def register_post():
    data = request.get_json()
    name = data['name']
    username = data['username']
    password = data['password']

    user_exist = DatabaseContext().check_user(username)

    if user_exist:
        return 'Username already in use', 400

    user_created = DatabaseContext().create_user(name, username, password)

    if not user_created:
        return 'Error creating user', 500
    else:
        return 'User created successfully', 200


@app.route('/groups')
def get_groups():
    id = request.args.get('id')
    groups = DatabaseContext().get_groups(id)

    group_list = []
    for group in groups:
        group = list(group)
        devices = DatabaseContext().get_devices(group[0])
        group_status = 'True' if len(devices) != 0 else 'False'
        device_status = 'False'
        for device in devices:
            status = DatabaseContext().get_device_status(device[0])
            if status is not None:
                device_status = 'False' if (datetime.now().timestamp() - status[1].timestamp()) > 600 else status[2]

            if device_status != 'True':
                group_status = 'False'
                break

        group.append(group_status)
        group_list.append(group)

    return render_template('groups.html', groups=group_list, user_id=id)


@app.route('/groups/new')
def new_group():
    user_id = request.args.get('user_id')
    return render_template('new_group.html', user_id=user_id)


@app.route('/groups/new', methods=['POST'])
def create_group():
    data = request.get_json()
    name = data['alias']
    user_id = data['user_id']
    description = data['description']

    group_created = DatabaseContext().create_group(name, description, user_id)

    if not group_created:
        return 'Error creating group', 500
    else:
        return 'Group created successfully', 200


@app.route('/devices')
def get_devices():
    user_id = request.args.get('user_id')
    group_id = request.args.get('group_id')
    devices = DatabaseContext().get_devices(group_id)

    device_list = []
    for device in devices:
        device = list(device)
        status = DatabaseContext().get_device_status(device[0])

        device.append('False')
        if status is not None:
            device[3] = 'False' if ((datetime.now().timestamp()-2*3600) - status[1].timestamp()) > 600 else status[2]

        device_list.append(device)

    return render_template('devices.html', devices=device_list, user_id=user_id, group_id=group_id)


@app.route('/devices/new')
def add_device():
    user_id = request.args.get('user_id')
    group_id = request.args.get('group_id')
    return render_template('new_device.html', group_id=group_id, user_id=user_id)


@app.route('/devices/new', methods=['POST'])
def create_device():
    data = request.get_json()

    eui = data['eui']
    mac = data['mac']
    name = data['alias']
    group_id = data['group_id']
    user_id = data['user_id']
    description = data['description']

    if DatabaseContext().is_device_registered(eui):
        return 'Device already registered', 400

    device_created = DatabaseContext().create_device(eui, mac, name, description, group_id, user_id)

    if not device_created:
        return 'Error creating device', 500
    else:
        return 'Device created successfully', 200


@app.route('/devices/<device_id>/restart')
def restart_device(device_id):
    if DatabaseContext().get_device(device_id) is None:
        return 'Device not found', 404
    else:
        send_message("AA==", device_id)  # AA== is 00 in base64
        DatabaseContext().log_action(device_id, 'reboot')
        return 'Reboot message published to queue', 200


@app.route('/devices/<device_id>/start')
def start_device(device_id):
    if DatabaseContext().get_device(device_id) is None:
        return 'Device not found', 404
    else:
        send_message("AQ==", device_id)  # AQ== is 01 in base64
        DatabaseContext().log_action(device_id, 'start')
        return 'Power message published to queue', 200


def send_message(command, eui):
    eui = f"eui-{eui.lower()}"
    endpoint = f"v3/server-snitch@ttn/devices/{eui}/down/push"
    message = '{"downlinks": [{"f_port": 1, "frm_payload": "' + command + '", "priority": "NORMAL"}]}'  # AQ== is 01 in base64
    publish.single(endpoint, message, hostname=HOSTNAME, auth=AUTH)


@app.route('/devices/<device_id>/trend')
def get_services(device_id):
    services = DatabaseContext().get_services(device_id)
    statuses = DatabaseContext().get_statuses(device_id)

    plots_data = []
    status_data = []

    for service in services:
        data_list = DatabaseContext().get_data(service[0], device_id)
        x = []
        y = []
        for data in data_list:
            if data[3] == 'float':
                x.append(float(data[1]))
            elif data[3] == 'int':
                x.append(int(data[1]))
            elif data[3] == 'bool':
                x.append(bool(data[1]))
            else:
                x.append(data[1])

            y.append(str(data[2]))

        plots_data.append((service[0], x, y))

    for status in statuses:
        value = True if status[2] == '1' or status[2] == 1 or status[2] == "True" else False
        #Check if status is older than 600 seconds
        if ((datetime.now().timestamp()-2+3600) - status[1].timestamp()) > 600:
            value = False

        status_data.append((status[0], status[1], value))

    return render_template('services.html', services=plots_data, statuses=status_data)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=443)
