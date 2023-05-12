from flask import Flask, render_template, request, jsonify

from Database.database import DatabaseContext

app = Flask(__name__)


@app.route('/login')
def login():
    return render_template("login.html")


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


@app.route('/groups')
def get_groups():
    id = request.args.get('id')
    groups = DatabaseContext().get_groups(id)

    return render_template('groups.html', groups=groups)


@app.route('/devices')
def get_devices():
    id = request.args.get('id')
    devices = DatabaseContext().get_devices(id)

    return render_template('devices.html', devices=devices)


@app.route('/services')
def get_services():
    id = request.args.get('id')
    services = DatabaseContext().get_services(id)

    plots_data = []

    for service in services:
        data_list = DatabaseContext().get_data(service[0], id)
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

    return render_template('services.html', services=plots_data)


if __name__ == '__main__':
    app.run(debug=True)
