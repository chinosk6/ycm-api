from flask import Flask, request, jsonify
from . import query
from . import ret_models

ycm_server = Flask(__name__)
ycm = query.Ycm()


def get_ip():
    """
    检查ip, 防止有人滥用api
    通常情况下, 获取请求者的ip可以使用以下方法的前两种。但是在部分特殊情况下, 前两种方法无法获取。
    请根据自己的实际情况选择。

    1.request.environ.get('HTTP_X_REAL_IP')
    2.request.remote_addr
    3.request.headers.get('X-Forwarded-For')
    """
    return request.headers.get('X-Forwarded-For')


@ycm_server.route('/add_car', methods=["GET", "POST"])
def add_car():
    uip = get_ip()
    token = request.args.get("token")
    car_type = request.args.get("car_type")
    room_id = request.args.get("room_id")
    description = request.args.get("description")
    data_from = request.args.get("data_from")
    creator_id = request.args.get("creator_id")
    more_info = request.args.get("more_info")

    if not ycm.check_permission(token, 1, uip):
        return jsonify(ret_models.return_status(403, "permission denied"))

    ret = ycm.add_car(car_type, room_id, description, data_from, creator_id, more_info)
    return jsonify(ret)


@ycm_server.route('/get_car', methods=["GET", "POST"])
def get_car():
    uip = get_ip()
    token = request.args.get("token")
    car_type = request.args.get("car_type")
    time_limit = request.args.get("time_limit")

    if not ycm.check_permission(token, 1, uip):
        return jsonify(ret_models.return_status(403, "permission denied"))

    ret = ycm.query_car(car_type, int(time_limit))
    return jsonify(ret)


@ycm_server.route('/add_token', methods=["GET", "POST"])
def add_token():
    token = request.args.get("token")
    userid = request.args.get("userid")
    username = request.args.get("username")
    description = request.args.get("description")
    permission = request.args.get("permission")
    uip = get_ip()

    if not ycm.check_permission(token, 3, uip):
        return jsonify(ret_models.return_status(403, "permission denied"))

    ret = ycm.add_token(userid, username, description, permission)
    return jsonify(ret)

@ycm_server.route('/update_token', methods=["GET", "POST"])
def update_token():
    token = request.args.get("token")
    token_set = request.args.get("token_set")
    uip = get_ip()

    if not ycm.check_permission(token, 1, uip):
        return jsonify(ret_models.return_status(403, "permission denied"))

    ret = ycm.update_token(token, token_set)
    return jsonify(ret)


@ycm_server.route("/add_car_table", methods=["GET", "POST"])
def add_car_table():
    token = request.args.get("token")
    uip = get_ip()
    car_name = request.args.get("car_name")
    car_alias = request.args.get("car_alias")

    if not ycm.check_permission(token, 2, uip):
        return jsonify(ret_models.return_status(403, "permission denied"))

    ret = ycm.create_car_table(car_name, car_alias)
    return jsonify(ret)


def start(host: str, port: int):
    ycm_server.run(host=host, port=port)
