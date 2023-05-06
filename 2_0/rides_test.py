import time

import redis

redis_client = redis.Redis(host='127.0.0.1', port=6379)

redis_client.set('my_var', 'Hello, Redis!')

redis_client.expire('my_var', 5)

my_var = redis_client.get('my_var')
print(my_var)

# 等待3分钟
time.sleep(6)

# 再次获取变量值
my_var = redis_client.get('my_var')
print(my_var)  # 返回None，因为变量已过期被删除
