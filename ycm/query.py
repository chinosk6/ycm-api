import sqlite3
import os
import time
from . import ret_models
import random
import string
import json
from typing import List
from threading import RLock
import re


def generate_randstring(num=8):
    value = ''.join(random.sample(string.ascii_letters + string.digits, num))
    return(value)

class YcmQuery:
    def __init__(self):
        spath = os.path.split(__file__)[0]
        self.spath = spath
        self.conn = sqlite3.connect(f"{spath}/data/car_numbers.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.lock = RLock()


    def car_types(self, car_type: str):
        cursor = self.cursor
        """
        传入值, 返回对应的表名. 若未找到, 则返回None
        :param car_type: 代号
        :return: 表名
        """
        with open(f"{self.spath}/data/table_names.json", "r", encoding="utf8") as f:
            ts = json.load(f)

        if car_type in ts:
            return ts[car_type]
        else:
            query = cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?",
                                   [car_type]).fetchone()
            if query[0] == 0:
                return None
            else:
                return car_type


    def create_car_table(self, table_name: str, table_alias):
        try:
            table_alias: List[str] = json.loads(table_alias)

            if type(table_alias) != list:
                return ret_models.return_status(1002, "'table_alias' must be an array(string)")
            if " " in table_name:
                return ret_models.return_status(1001, "Space is not allowed.Please use '_' instead")

            with open(f"{self.spath}/data/table_names.json", "r", encoding="utf8") as f:
                ts = json.load(f)
            for i in table_alias:
                if i not in ts:
                    if type(i) != str:
                        return ret_models.return_status(1002, "'table_alias' must be an array(string)")
                    elif " " in table_name:
                        return ret_models.return_status(1001, "Space is not allowed.Please use '_' instead")
                    else:
                        ts[i] = table_name

            with open(f"{self.spath}/data/table_names.json", "w", encoding="utf8") as f:
                f.write(json.dumps(ts))


            conn = self.conn
            cursor = self.cursor
            cursor.execute(f"CREATE TABLE {table_name} ('car_id' integer NOT NULL  PRIMARY KEY AUTOINCREMENT,"
                           "'room_id' text NOT NULL,"
                           "'description' text,"
                           "'data_from' text,"
                           "'creator_id' text,"
                           "'more_info' text,"
                           "'add_time' integer NOT NULL DEFAULT (STRFTIME('%s','now')));")
            conn.commit()


            return ret_models.return_status(0, "success")  # 建表成功
        except json.JSONDecodeError:
            return ret_models.return_status(1002, "'table_alias' must be an array(string)")
        except Exception as sb:
            return ret_models.return_status(500, repr(sb))


    def add_car(self, car_type: str, room_id: str, description: str, data_from: str, creator_id: str, more_info=""):
        try:
            self.lock.acquire()

            if None in [car_type, room_id, description, data_from, creator_id]:
                return ret_models.return_status(1003, "missing required parameters")

            _car_type = self.car_types(car_type)
            if _car_type is None:
                return ret_models.return_status(1001, "invalid car_type")  # 车类型错误

            if _car_type == "arcaea":
                room_id = room_id.upper()
                _r = re.findall("^[A-Z]{4}\\d{2}$", room_id)
                if len(_r) != 1:
                    return ret_models.return_status(1001, "invalid room_id")


            if description.replace(" ", "").isalnum():
                base_lenth = 50
            else:
                base_lenth = 30
            if len(description) > base_lenth:  # 简介过长
                return ret_models.return_status(1001, "description too long")

            conn = self.conn
            cursor = self.cursor

            qs = cursor.execute(f"SELECT car_id, room_id, description, data_from, creator_id, more_info, add_time"
                                f" FROM {_car_type} WHERE add_time > ? AND (room_id=? OR creator_id=?)",
                                [int(time.time()) - 120, room_id, creator_id]).fetchall()
            u_count = 0
            for query in qs:
                if query[1] == room_id:  # 撞车车
                    _car = ret_models.return_car(query[0], query[1], query[2], query[3], query[4], query[5], query[6])
                    return ret_models.return_status(1004, "ycl!", car=_car, car_type=_car_type)
                else:
                    u_count += 1
            if u_count >= 2:
                return ret_models.return_status(1005, "quantity limit")

            result = cursor.execute(f"INSERT INTO {_car_type} (room_id, description, data_from, creator_id, more_info, "
                                    f"add_time) VALUES (?, ?, ?, ?, ?, ?)",
                                    [room_id, description, data_from, creator_id, more_info, int(time.time())])

            conn.commit()
            return ret_models.return_status(0, "success", id=result.lastrowid, car_type=_car_type)  # 开车成功
        except Exception as sb:
            return ret_models.return_status(500, repr(sb))
        finally:
            self.lock.release()


    def query_car(self, car_type: str, time_seconds: int):
        time_seconds = 1200 if time_seconds > 1200 else time_seconds

        if time_seconds is None:
            return ret_models.return_status(1003, "missing param: time_seconds")

        _car_type = self.car_types(car_type)
        if _car_type is None:
            return ret_models.return_status(1001, "invalid car_type")

        cursor = self.cursor
        result = cursor.execute(f"SELECT car_id, room_id, description, data_from, creator_id, more_info, add_time "
                                f"FROM {_car_type} WHERE add_time > ?", [int(time.time()) - int(time_seconds)]).fetchall()
        if not result:
            return ret_models.return_status(404, "myc",  car_type=_car_type)  # 没有车!!!


        cars = []
        for car in result:
            _car = ret_models.return_car(car[0], car[1], car[2], car[3], car[4], car[5], car[6])
            cars.append(_car)

        return ret_models.return_status(0, "yc", cars=cars, car_type=_car_type)  # 有车!!!


class Ycm(YcmQuery):
    def __init__(self):
        super().__init__()

    def check_ip(self, ip, num=None, change_type="update"):
        """
        检查/更改ip
        :param ip: ip
        :param num: 变更数
        :param change_type: "update": 在原来的基础上 +num; "set": 设置次数为 num
        :return: 更新后的值。若未更新, 则显示原有值
        """
        if ip is None:
            print("waring: ip is None")
            return True

        conn = self.conn
        cursor = self.cursor

        query = cursor.execute("SELECT ip, wrong_times FROM wrong_control WHERE ip=?", [ip]).fetchone()
        if query is None:
            cursor.execute("INSERT INTO wrong_control (ip, wrong_times) VALUES (?, ?)", [ip, 0])
            conn.commit()
            wrong_times = 0
        else:
            wrong_times = query[1]

        if num is not None:
            wrong_times = num if change_type == "set" else wrong_times + num
            cursor.execute("UPDATE wrong_control SET wrong_times=? WHERE ip=?", [wrong_times, ip])
            conn.commit()

        return wrong_times


    def check_permission(self, token: str, need_permissions: int, ip: str) -> bool:
        # 普通权限 - 1, 高级权限 - 2, 管理员 - 3
        cursor = self.cursor
        if self.check_ip(ip) > 20:
            print(f"IP: {ip} 错误次数已达20, 禁止访问")
            return False

        result = cursor.execute("SELECT token, permissions FROM users WHERE token=?", [token]).fetchone()
        if result is None:
            self.check_ip(ip, 1, "update")  # ip错误次数+1
            return False
        elif result[1] < need_permissions:
            return False
        else:
            self.check_ip(ip, 0, "set")
            return True


    def add_token(self, userid="", username="", description="", permission=1):
        try:
            userid = "" if userid is None else userid
            username = "" if username is None else username
            description = "" if description is None else description
            permission = "" if permission is None else permission

            conn = self.conn
            cursor = self.cursor
            token = generate_randstring(18)
            cursor.execute("INSERT INTO users (userid, username, token, description, permissions) VALUES (?, ?, ?, ?, ?)",
                           [userid, username, token, description, permission])
            conn.commit()
            return ret_models.return_status(0, "success", token=token)  # 成功添加token
        except Exception as sb:
            return ret_models.return_status(500, repr(sb))

    def update_token(self, token_before: str, token_after: str):
        if token_after is None:
            token_after = generate_randstring(18)
        if len(token_after) < 12:
            return ret_models.return_status(1001, "The token needs at least 12 characters.")

        conn = self.conn
        cursor = self.cursor
        try:
            cursor.execute("UPDATE users SET token=? WHERE token=?", [token_after, token_before])
            conn.commit()
            return ret_models.return_status(0, "success", token=token_after)

        except Exception as sb:
            return ret_models.return_status(500, repr(sb))


    def __del__(self):
        self.cursor.close()
        self.conn.close()
