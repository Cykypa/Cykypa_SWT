import json
import random
import threading
import time

import redis

"""            
将数据存入Redis，并设计过期时间为60秒，随机取出一个            
"""
self_r = redis.Redis(host="127.0.0.1", port=6379)


class RedisDataHandler:

    def store_data(self):
        while True:
            time.sleep(4)
            data = {'key': 'Hello，Redis', 'timestamp': time.strftime("%Y-%M-%d %H:%M:%S", time.localtime())}
            # print(data)
            json_data = json.dumps(data)
            """            
            存储数据到Redis            
            """
            # 如果数据已经存在，直接跳过
            if self_r.get(json_data):
                print("重复")
                return
                # 存储数据并设置过期时间
            self_r.setex(json_data, 60, 'value')
            print("成功")


def get_random_data():
    """    从Redis中随机取出一个数据    """
    while True:
        time.sleep(1)
        # 获取所有的数据
        all_data = self_r.keys()

        print(all_data)
        # 随机选择一个数据
        if all_data:
            random_data = random.choice(all_data)
            print(f"取出：{json.loads(random_data.decode())}")
        else:
            print("取出失败")


if __name__ == '__main__':
    Redis_set = RedisDataHandler()
    t1 = threading.Thread(target=Redis_set.store_data)
    t2 = threading.Thread(target=get_random_data)
    t1.start()  # 开始线程
    t2.start()
