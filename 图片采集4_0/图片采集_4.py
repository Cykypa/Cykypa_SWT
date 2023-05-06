import json
import os
import random
import re
import threading
import time
import traceback
from datetime import datetime

import redis
import requests
from lxml import etree

from cookie_file import Next_cookie, config_IpPool, country_data_dict_list
from databaseinfo import ImageAuthor, DBSession

Next_url = "https://www.behance.net/v3/graphql"
with open('./config/fail.json', 'r') as f:
    fails = json.load(f)
# 创建一个队列对象
Next_cookie_file = Next_cookie()
config_IpPool_1 = config_IpPool()
self_r = redis.Redis(host="127.0.0.1", port=6379)
panduan = "正常"


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


# 爬取作者主页的所有作品
class ArtistHomepage:
    def main(self):
        session = DBSession()
        query = session.query(ImageAuthor).filter(ImageAuthor.uuid == "0").all()
        for Artist in query:
            print(f"作者：{Artist.author_name}，链接：{Artist.author_url}")
            try:
                self.wireless("MTI=", Artist.author_url)
                # self.First_page(Artist.author_url)
            except:
                print(traceback.format_exc())
                print("爬取作者主页的所有作品错误")
                break

    def wireless(self, end_cursor, url):
        data_da = {"end_cursor": end_cursor}
        while True:
            time.sleep(4)
            try:
                endCursor, headersda = self.Next(data_da["end_cursor"], url)
            except:
                print(traceback.format_exc())
                print("采集作者项目的Next函数出现问题")
                break
            data_da["end_cursor"] = endCursor
            if not headersda:
                print("作品已完成")
                data_info = {"url": url}
                StorageMysql("作品已完成", data_info)
                break

    def Next(self, after, url):
        match = re.search(r'(?<=/)[^/]+$', url)
        username = match.group(0)
        data = {
            "query": "\n  query GetProfileProjects($username: String, $after: String) {\n    user(username: $username) {\n      profileProjects(first: 12, after: $after) {\n        pageInfo {\n          endCursor\n          hasNextPage\n        }\n        nodes {\n          adminFlags {\n            mature_lock\n            privacy_lock\n            dmca_lock\n            flagged_lock\n            privacy_violation_lock\n            trademark_lock\n            spam_lock\n            eu_ip_lock\n          }\n          colors {\n            r\n            g\n            b\n          }\n          covers {\n            size_202 {\n              url\n            }\n            size_404 {\n              url\n            }\n            size_808 {\n              url\n            }\n          }\n          features {\n            url\n            name\n            featuredOn\n            ribbon {\n              image\n              image2x\n              image3x\n            }\n          }\n          fields {\n            id\n            label\n            slug\n            url\n          }\n          hasMatureContent\n          id\n          isFeatured\n          isHiddenFromWorkTab\n          isMatureReviewSubmitted\n          isOwner\n          isFounder\n          isPinnedToSubscriptionOverview\n          isPrivate\n          linkedAssets {\n            ...sourceLinkFields\n          }\n          linkedAssetsCount\n          sourceFiles {\n            ...sourceFileFields\n          }\n          matureAccess\n          modifiedOn\n          name\n          owners {\n            ...OwnerFields\n            images {\n              size_50 {\n                url\n              }\n            }\n          }\n          premium\n          publishedOn\n          stats {\n            appreciations {\n              all\n            }\n            views {\n              all\n            }\n            comments {\n              all\n            }\n          }\n          slug\n          tools {\n            id\n            title\n            category\n            categoryLabel\n            categoryId\n            approved\n            url\n            backgroundColor\n          }\n          url\n        }\n      }\n    }\n  }\n\n  \n  fragment sourceFileFields on SourceFile {\n    __typename\n    sourceFileId\n    projectId\n    userId\n    title\n    assetId\n    renditionUrl\n    mimeType\n    size\n    category\n    licenseType\n    moduleIds\n    unitAmount\n    currency\n    tier\n    hidden\n    extension\n    hasUserPurchased\n  }\n\n  \n  fragment sourceLinkFields on LinkedAsset {\n    __typename\n    moduleIds\n    name\n    premium\n    url\n    category\n    licenseType\n  }\n\n  \n  fragment OwnerFields on User {\n    displayName\n    hasPremiumAccess\n    id\n    isFollowing\n    isProfileOwner\n    location\n    locationUrl\n    url\n    username\n  }\n\n",
            "variables": {
                "username": f"{username}",
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

        if response.status_code == 200:
            response = response.json()
            endCursor = response["data"]["user"]["profileProjects"]["pageInfo"]["endCursor"]  # 下一页代码
            hasNextPage = response["data"]["user"]["profileProjects"]["pageInfo"]["hasNextPage"]  # 是否还有下一页，False就没有下一页了
            nodes = response["data"]["user"]["profileProjects"]["nodes"]
            nodes_url = []
            for node in nodes:
                nodes_url.append(node['url'])
            data_info = {"url": url, "opus_url": nodes_url}
            print(
                data_info
            )
            StorageMysql("修改", data_info)
            # print(nodes_url)
            return endCursor, hasNextPage
        else:
            raise ValueError("状态码错误")


# 写入日志信息
def log(classify, data):
    if classify == "采集日志":
        with open('./config/采集日志.txt', 'a+', encoding='utf-8') as f:
            f.write(f"{data}\n")
    elif classify == "链接请求失败":
        with open('./config/fail.json', 'w') as f:
            json.dump(data, f)


# 写入图片
def write(new_list, Image_link, return_word, author_url):
    if len(new_list) == 0:
        print(f"当前链接：{Image_link}，没有找到图片链接，跳过")
        fails.append(Image_link)
        log('链接请求失败', fails)
        end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        data = {
            "链接": Image_link, "时间": end_time, "状态": "采集失败",
            "失败原因": "详情页没有解析到图片链接"
        }
        log("采集日志", data)  # 写入采集日志
    else:
        print(f"共计：{len(new_list)} 张图片")
        # 创建当天的文件夹
        folder = time.strftime('%Y-%m-%d', time.localtime())
        if not os.path.exists(folder):
            os.mkdir(folder)
        # 创建具体的时间
        folder_1 = time.strftime('%H-%M-%S', time.localtime())
        filename = (os.getcwd() + f"/{folder}/{folder_1}").replace('\\', '/')
        if not os.path.exists(filename):
            os.mkdir(filename)
        Storage(folder, folder_1, Image_link, new_list, return_word, author_url)  # 写入数据
        for image_url in new_list:
            successful = False
            # 每张图片下载3次，每次请求等待十五秒
            for ni in range(3):
                print(f"第 {new_list.index(image_url) + 1} 张：第 {ni + 1} 次下载，正在写入...")
                if Download_image(image_url, folder, folder_1) == "下载成功":
                    successful = True
                    break
            if not successful:
                end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                data = {
                    "链接": Image_link, "时间": end_time, "状态": "采集失败",
                    "失败原因": f"第 {new_list.index(image_url) + 1} 张图片请求超时，跳过"
                }
                log("采集日志", data)  # 写入采集日志
                print("图片请求超时...跳过")


# 对每个详细页的数据进行爬取
def second_request(link_lists, author_url):
    if len(link_lists) == 0:
        print("link_lists列表为空，停止")
    else:
        for Image_link in link_lists:
            print(f"共计：{len(link_lists)}，当前：{link_lists.index(Image_link) + 1} 个，当前链接：{Image_link}")
            time.sleep(0.1)
            try:
                if config_IpPool_1['enable'] == "Yes":
                    print("使用代理IP")
                    response = requests.get(
                        Image_link, proxies=mysql_ip_pool()
                    )
                else:
                    print("不使用代理IP")
                    response = requests.get(
                        Image_link
                    )
                html = response.text
                selector = etree.HTML(html)
                # 调用提取文本的方法
                return_word = Extraction_tools(selector)
                if return_word == "获取文本失败":
                    end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    data = {
                        "链接": Image_link, "时间": end_time, "状态": "采集失败",
                        "失败原因": return_word
                    }
                    log("采集日志", data)  # 写入采集日志
                else:
                    img_src_list = selector.xpath('//*[@id="project-modules"]//img/@src')  # 链接
                    img_src_list = img_src_list + selector.xpath('//*[@id="project-modules"]//img/@data-src')
                    # print(img_src_list)  # 打印检查
                    to_remove = 'https://a5.behance.net'  # 排除a5的链接，a5不是
                    new_list = [x for x in img_src_list if to_remove not in x]  # 图片的去重
                    print("成功，准备写入图片")
                    print(f"图片链接：{new_list}，项目链接：{Image_link}，文字：{return_word}")  # 打印检查
                    write(new_list, Image_link, return_word, author_url)
            except:
                # 出现请求失败会将文件写入
                fails.append(Image_link)
                log('链接请求失败', fails)
                end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                data = {
                    "链接": Image_link, "时间": end_time, "状态": "采集失败",
                    "失败原因": traceback.format_exc()
                }
                log("采集日志", data)  # 写入采集日志
                print(traceback.format_exc())
                print(f"当前链接：{Image_link}，请求出现问题，跳过")
                time.sleep(1)
                pass
            time.sleep(0.5)


# 获取并存入代理ip
class IpPool:

    def run(self, ):
        while True:
            print("获取代理IP执行中，每10秒执行一次")
            data = self.ip_spider()
            """测试代码"""
            # data = {'key': 'Hello，Redis', 'timestamp': time.strftime("%Y-%M-%d %H:%M:%S", time.localtime())}
            print(data)
            if data == "Insufficient traffic, please recharge":
                break
            else:
                self.add_data_to_set(json.dumps(data))
                # print(f"存入：{data}")
                time.sleep(10)

    def ip_spider(self):
        url = config_IpPool_1['url']
        response = requests.get(url).json()
        if response['code'] == 211:
            print(response['msg'])
            return "Insufficient traffic, please recharge"
        print(response)
        sj1 = response["data"][0]["ip"]
        sj2 = response["data"][0]["port"]
        proxyMeta = f"http://{config_IpPool_1['user']}:{config_IpPool_1['password']}@%(host)s:%(port)s" % {  # 账密验证
            "host": sj1,
            "port": sj2,
        }
        print("获取代理为：", proxyMeta)
        proxysdata = {
            'http': proxyMeta,
            'https': proxyMeta
        }
        return proxysdata

    def add_data_to_set(self, json_data):
        # 如果数据已经存在，直接跳过
        if self_r.get(json_data):
            print(f"代理IP：{json_data}，重复跳过")
            return

        # 存储数据并设置过期时间
        self_r.setex(json_data, 120, 'value')
        print(f"代理IP：{json_data}，存入成功")


# 提取出需要的文字
def Extraction_tools(selector):
    try:
        # 所有者
        owner = selector.xpath(
            '//a[@class="UserInfo-userName-BoH qa-user-link e2e-ProjectOwnersInfo-user-link"]/text()'
        )
        # 项目名
        Project_name = selector.xpath(
            'normalize-space(//*[@id="site-content"]/div/div[1]/div/div[2]/div[1]/figcaption/span/text())'
        )
        # 获取赞赏数
        appreciations = selector.xpath(
            "normalize-space(//div[@class='ProjectInfo-projectStat-xLj beicons-pre beicons-pre-thumb e2e-ProjectInfo-projectStat-appreciations']//span/text())"
        )
        # 获取浏览量
        Views = selector.xpath(
            "normalize-space(//div[@class='ProjectInfo-projectStat-xLj beicons-pre beicons-pre-eye']//span/text())"
        )
        # 获取评论量
        comments = selector.xpath(
            "normalize-space(//div[@class='ProjectInfo-projectStat-xLj beicons-pre beicons-pre-comment qa-project-comment-count']//span/text())"
        )
        # 获取发布时间
        publish = selector.xpath(
            "normalize-space(//div[@class='ProjectInfo-projectPublished-Exm']//time/text())"
        )
        # 获取工具
        tools = selector.xpath("//div[@class='ProjectTools-section-k_L e2e-Project-Tools-tools']//li")
        tools_list = []
        for tool in tools:
            if tool.xpath(".//p"):
                tool_text = tool.xpath("normalize-space(.//p/text())")
            else:
                tool_text = tool.xpath("normalize-space(./a/text())")
            tools_list.append(tool_text)
            # 使用filter()函数删除空列表
        tools_list = list(filter(None, tools_list))
        # 获取创意领域
        fields = selector.xpath("//div[@class='ProjectTools-section-k_L e2e-Project-Tools-creative-fields']//li")
        field_list = []
        for field in fields:
            if field.xpath(".//p"):
                field_text = field.xpath("normalize-space(.//p/text())")
            else:
                field_text = field.xpath("normalize-space(./a/text())")
            field_list.append(field_text)
        field_list = list(filter(None, field_list))
        # 获取标签
        tags = selector.xpath(
            "//ul[@class='ProjectTags-projectTags-wWY ProjectTags-usePillShapedTags-O5E js-project-tags ProjectInfo-infoBlocks-jRx ProjectInfo-projectTags-c4w']//li/a/text()"
        )

        Image_link_data = {
            "所有者": owner, "项目名": Project_name, "赞赏数": appreciations,
            "浏览量": Views, "评论量": comments, "发布时间": publish, "工具": tools_list,
            "创意领域": field_list, "标签": tags,
        }
        # print(Image_link_data)
        print("获取文本成功")
        return Image_link_data
    except:
        return "获取文本失败"


# 存入json
def Storage(folder, folder_1, Image_link, new_list, return_word, author_url):
    metadata = {"项目链接": Image_link, "作家链接": author_url, "图片链接": new_list, "文字": return_word, }
    with open(f"{folder}/{folder_1}/metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False)
    end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    data = {
        "链接": Image_link, "时间": end_time, "状态": "采集成功",
    }
    log("采集日志", data)  # 写入采集日志


# 下载图片
def Download_image(image_url, folder, folder_1):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }
    try:
        if config_IpPool_1['enable'] == "Yes":
            print("使用代理IP")
            r = requests.get(image_url, headers=headers, timeout=15, proxies=mysql_ip_pool())
        else:
            print("不使用代理IP")
            r = requests.get(image_url, headers=headers, timeout=15)
        down_time = int(time.time() * 1000)
        with open(f"{folder}/{folder_1}/{down_time}.jpg", mode="wb") as f:
            f.write(r.content)
        return "下载成功"
    except:
        return "下载失败"


# 列表去重
def removing_duplicated(lst):
    print("已去重")
    return list(set(lst))


# 将信息存入MySQL
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


# 爬取作者信息
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


# 启动获取代理ip方法
def run_IpPool():
    ip = IpPool()
    ip.run()


def deadlines(year, mouth, day, hour):
    now = datetime.now().timestamp()
    expire = datetime(year, mouth, day, hour, 0).timestamp()
    res = expire - now
    if res < 0:
        raise Exception


# 启动采集艺术家主页链接
def run_AuthorSpider():
    time.sleep(10)
    AuthorSpider1 = AuthorSpider()
    AuthorSpider1.run()


# 启动采集艺术家所有项目链接
def run_ArtistHomepage():
    time.sleep(10)
    ArtistHomepage1 = ArtistHomepage()
    ArtistHomepage1.main()


# 启动采集艺术家所有项目的图片
def Download_Artist_image():
    time.sleep(10)
    session = DBSession()
    query = session.query(ImageAuthor).filter(ImageAuthor.uuid == "1").all()
    for i in query:
        print(f"当前下载的是：{i.author_name}")
        second_request(json.loads(i.opus_url), i.author_url)


if __name__ == '__main__':
    deadlines(2023, 5, 10, 0)  # 调用方法
    t1 = threading.Thread(target=run_AuthorSpider)  # 爬取作者主页链接
    t2 = threading.Thread(target=run_ArtistHomepage)  # 爬取作者所有作品
    t3 = threading.Thread(target=Download_Artist_image)  # 下载图片
    t4 = threading.Thread(target=run_IpPool)  # 启动代理IP
    if config_IpPool_1['enable'] == "Yes":
        t4.start()
    t3.start()
    t2.start()
    t1.start()  # 开始线程
    # t5 = threading.Thread(target=mysql_ip_pool)  # 取出代理IP
    #     # time.sleep(0.5)
    #     # t5.start()
