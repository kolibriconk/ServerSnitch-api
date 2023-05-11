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


if __name__ == '__main__':
    app.run(debug=True)
