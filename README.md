# ycm-api

- 简易的查车车API



# 自行部署

- 确保您拥有`python3`环境
- 需要以下包: `pip install -r requirements.txt`

```
Flask~=2.0.1
```

- 运行: 
  - 编辑`app.py`内的ip和端口
  - `python app.py`



# API说明

### 查车车

- 接口: `/get_car`
- 需要权限: `1`

| 参数       | 类型   | 说明                          | 可选的 |
| ---------- | ------ | ----------------------------- | ------ |
| token      | string | 身份验证                      | ×      |
| car_type   | string | 车车类型                      | ×      |
| time_limit | int    | 获取x秒内的车, 最多获取1200秒 | ×      |

- 返回值

| 参数    | 类型        | 说明         |
| ------- | ----------- | ------------ |
| code    | int         | 状态码       |
| message | string      | 说明         |
| cars    | string[car] | 车车信息数组 |



### 添加车车

- 接口: `/add_car`
- 需要权限: `2`

| 参数        | 类型   | 说明                  | 可选的 |
| ----------- | ------ | --------------------- | ------ |
| token       | string | 身份验证              | ×      |
| car_type    | string | 车车类型              | ×      |
| room_id     | string | 房间id                | ×      |
| description | string | 房间描述              | ×      |
| data_from   | string | 数据来源(平台, bot等) | ×      |
| creator_id  | string | 创建者id              | ×      |
| more_info   | string | 更多信息(暂时没用)    | √      |

- 返回值

| 参数    | 类型   | 说明                   |
| ------- | ------ | ---------------------- |
| code    | int    | 状态码                 |
| message | string | 说明                   |
| id      | int    | 该车的内部id, 非车牌号 |



### 添加车车类型

- 接口: `/add_car_table`

| 参数      | 类型          | 说明           | 可选的 |
| --------- | ------------- | -------------- | ------ |
| token     | string        | 身份验证       | ×      |
| car_name  | string        | 车车类型(全称) | ×      |
| car_alias | array[string] | 车车别称       | ×      |

- 返回值

| 参数    | 类型   | 说明                   |
| ------- | ------ | ---------------------- |
| code    | int    | 状态码                 |
| message | string | 说明                   |




### 添加token

- 接口: `/add_token`
- 需要权限: `3`

| 参数        | 类型   | 说明                                                         | 可选的 |
| ----------- | ------ | ------------------------------------------------------------ | ------ |
| token       | string | 自己的token                                                  | ×      |
| userid      | string | 用户id                                                       | ×      |
| username    | string | 用户名                                                       | √      |
| description | string | 简单描述                                                     | √      |
| permission  | int    | 此token的权限等级<br>可填入`1`/`2`/`3`<br>数字越大, 权限越高 | ×      |



# 返回数据说明

## car

| 参数        | 类型   | 说明               |
| ----------- | ------ | ------------------ |
| id          | int    | 该车内部ID         |
| room_id     | string | 该车车牌号(房间号) |
| description | string | 车辆简介           |
| data_from   | string | 数据来源           |
| creator_id  | string | 创建者ID           |
| more_info   | string | 更多信息           |
| add_time    | int    | 车牌添加时间戳     |

------

## 状态码说明

| 状态码 | 说明              |
| ------ | ----------------- |
| 0      | 请求正常处理/有车 |
| 403    | 没有权限          |
| 404    | 没有车            |
| 500    | 服务器内部错误    |
| 1001   | 参数输入错误      |
| 1002   | 参数类型错误      |
| 1003   | 缺少必要参数      |

