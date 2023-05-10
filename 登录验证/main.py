from flask import Flask, request
from controller.adminController import Controller as admin

app = Flask(__name__)
admin = admin()


@app.route('/')
def hello_world():
    return '后端接口已启动成功！'


@app.route('/api/admin/login', methods=["POST"])
def adminLogin():
    return admin.login(request)


@app.route('/api/admin/info', methods=["GET"])
def adminInfo():
    return admin.getInfo(request)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        # port='5000',
        debug=True
    )
