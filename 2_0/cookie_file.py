import random
import time

import redis
import requests

from database import ImageSpiderIp1, DBSession


class IpPool:

    def delMySQL(self):
        session = DBSession()
        del_timestamp = int(time.time() * 1000)
        IP_list = session.query(ImageSpiderIp1).filter(ImageSpiderIp1.end_time < del_timestamp).all()
        if len(IP_list) == 0:
            print("没有过期的IP代理")
            session.close()
        else:
            for i in IP_list:
                session.query(ImageSpiderIp1).filter(ImageSpiderIp1.id == i.id).delete()
                session.commit()
                print(f"已删除：{i.ip}")
            session.close()

    # 查询是否有相等的
    def Search(self, proxysdata):
        print("开始查询")
        session = DBSession()
        IP_list = session.query(ImageSpiderIp1).filter(ImageSpiderIp1.ip == proxysdata).all()
        session.close()
        if len(IP_list) > 0:
            print("数据库有相同的IP代理")
            return "Yes"
        else:
            print("统一添加")
            return 'No'

    # 存入
    def storage(self, proxysdata):
        print("开始存入")

        session = DBSession()
        # 获取当前时间的13位时间戳
        current_timestamp = int(round(time.time() * 1000))
        future_timestamp = int(round(time.time() * 1000)) + 3 * 60 * 1000
        data = ImageSpiderIp1(
            ip=str(proxysdata), start_time=current_timestamp, end_time=future_timestamp,
        )
        session.add(data)
        session.commit()
        session.close()
        print(f"{proxysdata}：插入成功。")

    def ip_spider(self):
        url = 'http://api.ipipgo.com/ip?cty=00&c=1&pt=2&ft=json&pat=\n&rep=1&key=d386a16d&ts=3'
        response = requests.get(url).json()
        sj1 = response["data"][0]["ip"]
        sj2 = response["data"][0]["port"]
        return f"{sj1}:{sj2}"
        # return proxysdata

    def run(self):
        proxysdata = self.ip_spider()
        # self.storage(proxysdata)  # 在存入
        if self.Search(proxysdata) == "No":  # 先查询
            self.storage(proxysdata)  # 在存入
        else:
            print("改代理已存在")
        self.delMySQL()  # 最后删除


redis_client = redis.Redis(host='127.0.0.1', port=6379)


class ReidsClass:

    def storage(self):
        while True:
            print('执行中...')
            # 每隔10秒向列表中添加一个随机数
            value = random.randint(0, 100)
            redis_client.lpush('my_list', value)
            redis_client.expire('my_list', 2)
            print('my_list', value)
            time.sleep(1)


if __name__ == '__main__':
    # IP_Pool = IpPool()
    # IP_Pool.run()
    ReidsClass = ReidsClass()
    ReidsClass.storage()
