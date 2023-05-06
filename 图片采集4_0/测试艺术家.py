import json
import random
import time
import traceback

import redis
import requests

from cookie_file import config_IpPool, country_data_dict_list, Next_cookie
from databaseinfo import ImageAuthor, DBSession

Next_url = "https://www.behance.net/v3/graphql"
with open('./config/fail.json', 'r') as f:
    fails = json.load(f)
# 创建一个队列对象
Next_cookie_file = Next_cookie()
config_IpPool_1 = config_IpPool()
self_r = redis.Redis(host="127.0.0.1", port=6379)
panduan = "正常"


def removing_duplicated(lst):
    print("已去重")
    return list(set(lst))


def StorageMysql(info, data_info):
    session = DBSession()
    if info == "修改":
        # print(f"调用修改函数：{data_info}")
        session = DBSession()
        ImageAuthor_opus_url = session.query(ImageAuthor).filter(
            ImageAuthor.author_url == data_info['url']
        ).all()
        if ImageAuthor_opus_url[0].opus_url:
            ImageAuthor_opus_url_list = json.loads(ImageAuthor_opus_url[0].opus_url)  # 原来的
            data_info_opus_url_1 = ImageAuthor_opus_url_list + data_info['opus_url']  # 合并
            data_info_opus_url = removing_duplicated(data_info_opus_url_1)
            session.query(ImageAuthor).filter(ImageAuthor.author_url == data_info['url']).update(
                {
                    ImageAuthor.opus_url: json.dumps(data_info_opus_url),
                }
            )
            session.commit()
            session.close()
            print("1：修改成功")
        else:
            session.query(ImageAuthor).filter(ImageAuthor.author_url == data_info['url']).update(
                {
                    ImageAuthor.opus_url: json.dumps(data_info['opus_url']),
                }
            )
            session.commit()
            session.close()
            print("2：修改成功")

    elif info == "保存":
        record = session.query(ImageAuthor).filter(ImageAuthor.author_url == data_info['url']).first()
        if not record:
            data = ImageAuthor(
                author_url=data_info['url'], author_name=data_info['displayName'], uuid="0"
            )
            session.add(data)
            session.commit()
            print(f"1：艺术家：{data_info['displayName']}信息保存成功")
        else:
            print(f"艺术家：{data_info['displayName']}已存在")
        session.close()
    elif info == "作品已完成":
        session.query(ImageAuthor).filter(ImageAuthor.author_url == data_info['url']).update(
            {
                ImageAuthor.uuid: "1",
            }
        )
        session.commit()
        session.close()


def mysql_ip_pool():
    """
        从Redis中随机取出一个数据
    """
    while True:
        # 获取所有的数据
        all_data = self_r.keys()
        # print(f"所有数据：{all_data}")
        # 随机选择一个数据
        if all_data:
            random_data = random.choice(all_data)
            print(f"取出：{json.loads(random_data.decode())}")
            return json.loads(random_data.decode())
        else:
            if len(all_data) == 0:
                print("代理IP，取出失败，Redid数据库为空，请检查代理IP费用")
            else:
                print("代理IP，取出失败，原因不明，以下是报错信息")
                print(traceback.format_exc())
            time.sleep(1)


class AuthorSpider:

    def AuthorSpiderNext(self, after, country):
        data = {
            "query": "\n  query GetHireSearchResults($query: query, $filter: SearchResultFilter, $first: Int!, $after: String) {\n    search(query: $query, type: USER, filter: $filter, first: $first, after: $after) {\n      pageInfo {\n        hasNextPage\n        endCursor\n      }\n      nodes {\n        ... on User {\n          ...hirePageUserFields\n        }\n      }\n      metaContent {\n        ...metaContentFields\n      }\n    }\n  }\n\n  \n  fragment hirePageUserFields on User {\n    id\n    username\n    url\n    isProfileOwner\n    images {\n      size_50 {\n        url\n      }\n      size_100 {\n        url\n      }\n      size_115 {\n        url\n      }\n      size_138 {\n        url\n      }\n      size_230 {\n        url\n      }\n      size_276 {\n        url\n      }\n    }\n    displayName\n    location\n    isFollowing\n    allowsContactFromAnyone\n    isMessageButtonVisible\n    availabilityInfo {\n      availabilityTimeline\n      buttonCTAType\n      compensationMin\n      currency\n      isAvailableFullTime\n      isLookingForRemote\n      isAvailableFreelance\n    }\n    stats {\n      appreciations\n      views\n      followers\n    }\n    projects(first: 4) {\n      nodes {\n        name\n        url\n        slug\n        covers {\n          size_404 {\n            url\n            width\n            height\n          }\n          size_404_webp {\n            url\n            width\n            height\n          }\n        }\n      }\n    }\n  }\n\n  \n  fragment metaContentFields on SearchMetaContent {\n    csam {\n      isCSAMViolation\n      description\n      helpResource\n      reportingOption\n    }\n    totalEntityCount\n  }\n\n",
            "variables": {
                "query": "",
                "filter": {
                    "userAvailability": {
                        "isAvailableFullTime": True,
                        "isAvailableFreelance": True,
                        "isLookingForRemote": False
                    },
                    "country": f"{country}",
                    "sort": "recommended"
                },
                "first": 48,
                "after": f"{after}"
            }
        }
        data = json.dumps(data, separators=(',', ':'))
        if config_IpPool_1['enable'] == "Yes":
            print("使用代理IP")
            response = requests.post(
                Next_url,
                headers=Next_cookie_file['Next_headers'],
                data=data,
                proxies=mysql_ip_pool()
            )
        else:
            print("不使用代理IP")
            response = requests.post(
                Next_url,
                headers=Next_cookie_file['Next_headers'],
                data=data
            )
            print(response.text)
        if response.status_code == 200:
            print("拿取数据成功，清理中...")
            response_json = response.json()
            # print(response_json)  # 打印检查
            hasNextPage = response_json["data"]["search"]["pageInfo"]["hasNextPage"]  # 是否有下一页
            endCursor = response_json["data"]["search"]["pageInfo"]["endCursor"]  # 下一页请求参数
            # 艺术家列表
            nodes = response_json["data"]["search"]["nodes"]
            if nodes:
                for node in nodes:
                    url = node["url"]  # 艺术家主页
                    displayName = node["displayName"]  # 艺术家名称
                    location = node["location"]  # 艺术家国际
                    user_data = {"艺术家主页": url, "艺术家名称": displayName, "艺术家国际": location, }
                    try:
                        data_info = {"url": url, "displayName": displayName}
                        StorageMysql("保存", data_info)
                    except:
                        print(f"写入失败：{user_data}")
            else:
                print("数据列表为空，当前城市创作者采集完毕")
            return endCursor, hasNextPage
        else:
            print("创作者的主页链接返回状态码不正确")
            return '创作者的主页链接返回状态码不正确', False

    def run(self):
        # OTkyMw==  倒数第二页
        # OTk3Mg==  最后一页，大概只有202页
        # MjU=  第一页
        after = {"after": "MjU="}
        for country in country_data_dict_list():
            i = 0
            while True:
                i = i + 1
                afte1r, panduan1 = self.AuthorSpiderNext(after['after'], country['value'])
                after['after'] = afte1r
                print(f"下一页请求参数：{after['after']}")
                random_int = random.randint(1, 10)
                print(f"当前城市：{country['label']}，艺术家第 {i} 页写入成功\n")
                if not panduan1:
                    print("当前国家采集完成，等待60再继续。。。。")
                    time.sleep(60)
                    break
                print(f"休息：{random_int}秒，在继续。。。")
                time.sleep(random_int)


if __name__ == '__main__':
    AuthorSpider1 = AuthorSpider()
    AuthorSpider1.run()
