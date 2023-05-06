import json
import os
import re
import threading
import time

import redis
import requests
from lxml import etree

from cookie_file import cookie_file, Next_cookie

with open('./config/fail.json', 'r') as f:
    fails = json.load(f)

redis_client = redis.Redis(host='127.0.0.1', port=6379)


#  取出代理ip
def mysql_ip_pool():
    data = redis_client.srandmember('my_set')
    IP_data = data.decode('utf-8') if data else None
    IP_data = json.loads(IP_data)
    return IP_data


# 写入日志信息
def log(classify, data):
    if classify == "采集日志":
        with open('./config/采集日志.txt', 'a+', encoding='utf-8') as f:
            f.write(f"{data}\n")
    elif classify == "链接请求失败":
        with open('./config/fail.json', 'w') as f:
            json.dump(data, f)


# 获取并存入代理ip
class IpPool:
    def run(self):
        redis_client.flushall()  # 删除以前的数据
        while True:
            print("执行中，每15秒执行一次")
            data = json.dumps(self.ip_spider())
            self.add_data_to_set(data)
            print(f"存入：{data}")
            time.sleep(15)

    def ip_spider(self):
        url = 'http://api.ipipgo.com/ip?cty=00&c=1&pt=2&ft=json&pat=\n&rep=1&key=d386a16d&ts=3'
        response = requests.get(url).json()
        print(response)
        if response['code'] == 211:
            print(response['msg'])
            raise ValueError(f"{response['msg']}")
        else:
            sj1 = response["data"][0]["ip"]
            sj2 = response["data"][0]["port"]
            proxyMeta = "http://4a565f:c3b53d78@%(host)s:%(port)s" % {  # 账密验证
                "host": sj1,
                "port": sj2,
            }
            print("获取代理为：", proxyMeta)
            proxysdata = {
                'http': proxyMeta,
                'https': proxyMeta
            }
            return proxysdata

    def add_data_to_set(self, data):
        if not redis_client.sismember('my_set', data):
            redis_client.sadd('my_set', data)
            redis_client.expire('my_set:' + data, 120)  # 将过期时间设置在每个元素上，过期时间为两分钟

    def check_data_in_set(self, data):
        return redis_client.sismember('my_set', data)


# 提取出需要的文字
def Extraction_tools(selector):
    try:
        # 所有者
        owner = selector.xpath(
            '//a[@class="UserInfo-userName-BoH qa-user-link e2e-ProjectOwnersInfo-user-link"]/text()'
        )

        # owner = selector.xpath(
        #     'normalize-space(//a[@class="UserInfo-userName-BoH qa-user-link e2e-ProjectOwnersInfo-user-link"]/text())'
        # )
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
def Storage(folder, folder_1, Image_link, new_list, return_word):
    metadata = {"项目链接": Image_link, "图片链接": new_list, "文字": return_word, }
    with open(f"{folder}/{folder_1}/metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False)
    end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    data = {
        "链接": Image_link, "时间": end_time, "状态": "采集成功",
    }
    log("采集日志", data)  # 写入采集日志


# def Storage(Image_link, new_list, return_word):
#     session = DBSession()
#     try:
#         existed_data = session.query(ClassImage).filter_by(Project_link=Image_link).first()
#         if existed_data:
#             # print(f"{Image_link}：项目链接重复，不存储跳过")
#             return "项目链接重复，不存储跳过"
#         else:
#             data = ClassImage(
#                 Project_link=Image_link, Image_link=json.dumps(new_list), Image_writing=json.dumps(return_word),
#             )
#             session.add(data)
#             session.commit()
#             end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
#             data = {
#                 "链接": Image_link, "时间": end_time, "状态": "采集成功",
#             }
#             log("采集日志", data)  # 写入采集日志
#             # print(f"{Image_link}，所有图片写入成功")
#             return f"{Image_link}，所有图片写入成功"
#     except Exception as e:
#         print(f"{Image_link}：存储数据失败，错误信息：{e}")
#         return f"{Image_link}：存储数据失败，错误信息：{e}"
#     finally:
#         session.close()


# 下载图片信息
def Download_image(image_url, folder, folder_1):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(image_url, headers=headers, timeout=15)
        down_time = int(time.time() * 1000)
        with open(f"{folder}/{folder_1}/{down_time}.jpg", mode="wb") as f:
            f.write(r.content)
        return "下载成功"
    except:
        return "下载失败"


# 爬取图片信息
class ImageSpider:
    def __init__(self):
        self.headers = {
            "authority": "www.behance.net",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "max-age=0",
            "sec-ch-ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        }

    # 第一页
    def First_page(self):
        time.sleep(5)  # 要让代理IP先启动，不然没有代理IP
        url = "https://www.behance.net/search/projects"
        params = {
            "tracking_source": "typeahead_nav_suggestion_filter"
        }
        response = requests.get(url, headers=self.headers, cookies=cookie_file(), params=params)
        if response.status_code == 200:
            print(f"第一页成功")
            end_cursor = "NDk="
            pattern = r'"endCursor":"([A-Za-z0-9+/=]+)"'
            match = re.search(pattern, response.text)
            if match:
                print("匹配到endCursor")
                end_cursor = match.group(1)
                print(f"第一页返回：{end_cursor}")
            else:
                print("没有找到endCursor，使用默认endCursor")
            try:
                html = etree.HTML(response.content)
                link_lists = list(set(html.xpath('//a[@title="项目的链接"]/@href')))
                print(f"以匹配的项目链接，共计：{len(link_lists)} 个")
                self.second_request(link_lists, end_cursor)
            except:
                print("匹配项目链接失败，请重试...")
        else:
            print("第一页返回状态码错误，请重试...")

    # 下一页
    def Next(self, endCursor):
        Next_cookie_file = Next_cookie()
        url = "https://www.behance.net/v3/graphql"
        data = {
            "query": "\n      query GetProjectSearchResults($query: query, $filter: SearchResultFilter, $first: Int!, $after: String) {\n        search(query: $query, type: PROJECT, filter: $filter, first: $first, after: $after) {\n          pageInfo {\n            hasNextPage\n            endCursor\n          }\n          nodes {\n            ... on Project {\n              id\n              colors {\n                r\n                g\n                b\n              }\n              isMatureReviewSubmitted\n              linkedAssetsCount\n              name\n              premium\n              isPrivate\n              publishedOn\n              isFounder\n              isFeatured\n              modifiedOn\n              adminFlags {\n                mature_lock\n                privacy_lock\n                dmca_lock\n                flagged_lock\n                privacy_violation_lock\n                trademark_lock\n                spam_lock\n                eu_ip_lock\n              }\n              features {\n                featuredOn\n                url\n                name\n                ribbon {\n                  image\n                  image2x\n                  image3x\n                }\n              }\n              slug\n              stats {\n                views {\n                  all\n                }\n                appreciations {\n                  all\n                }\n                comments {\n                  all\n                }\n              }\n              url\n              fields {\n                label\n              }\n              linkedAssets {\n                ...sourceLinkFields\n              }\n              sourceFiles {\n                ...sourceFileFields\n              }\n              matureAccess\n              hasMatureContent\n              owners {\n                ...OwnerFields\n                images {\n                  size_50 {\n                    url\n                  }\n                  size_100 {\n                    url\n                  }\n                  size_115 {\n                    url\n                  }\n                  size_138 {\n                    url\n                  }\n                  size_230 {\n                    url\n                  }\n                  size_276 {\n                    url\n                  }\n                }\n              }\n              covers {\n                size_original {\n                  url\n                }\n                size_max_808 {\n                  url\n                }\n                size_808 {\n                  url\n                }\n                size_404 {\n                  url\n                }\n                size_202 {\n                  url\n                }\n                size_230 {\n                  url\n                }\n                size_115 {\n                  url\n                }\n                size_original_webp {\n                  url\n                }\n                size_max_808_webp {\n                  url\n                }\n                size_808_webp {\n                  url\n                }\n                size_404_webp {\n                  url\n                }\n                size_202_webp {\n                  url\n                }\n                size_230_webp {\n                  url\n                }\n                size_115_webp {\n                  url\n                }\n              }\n            }\n          }\n          metaContent {\n            toolCard {\n              cta {\n                text\n                url\n              }\n              description\n              links {\n                text\n                url\n                type\n              }\n              slug\n              title\n            }\n            schoolCard {\n              cta {\n                text\n                url\n              }\n              description\n              slug\n            }\n            csam {\n              isCSAMViolation\n              description\n              helpResource\n              reportingOption\n            }\n            followableTag {\n              isFollowing\n              tag {\n                id\n                title\n              }\n            }\n          }\n        }\n      }\n\n      \n  fragment sourceLinkFields on LinkedAsset {\n    __typename\n    moduleIds\n    name\n    premium\n    url\n    category\n    licenseType\n  }\n\n      \n  fragment sourceFileFields on SourceFile {\n    __typename\n    sourceFileId\n    projectId\n    userId\n    title\n    assetId\n    renditionUrl\n    mimeType\n    size\n    category\n    licenseType\n    moduleIds\n    unitAmount\n    currency\n    tier\n    hidden\n    extension\n    hasUserPurchased\n  }\n\n      \n  fragment OwnerFields on User {\n    displayName\n    hasPremiumAccess\n    id\n    isFollowing\n    isProfileOwner\n    location\n    locationUrl\n    url\n    username\n  }\n\n    ",
            "variables": {
                "filter": {},
                "first": 48,
                "after": f"{endCursor}"
            }
        }
        data = json.dumps(data, separators=(',', ':'))
        response = requests.post(
            url,
            headers=Next_cookie_file['Next_headers'],
            cookies=Next_cookie_file['Next_cookies'],
            data=data
        ).json()
        link_lists = []
        endCursor = response["data"]["search"]["pageInfo"]["endCursor"]
        for i in response["data"]["search"]["nodes"]:
            link_lists.append(i['url'])
        print(f"返回：endCursor：{endCursor}，link_lists：{link_lists}")
        self.second_request(link_lists, endCursor)

    # 对每个详细页的数据进行爬取
    def second_request(self, link_lists, endCursor):
        if len(link_lists) == 0:
            print("link_lists列表为空，停止")
        else:
            for Image_link in link_lists:
                print(f"共计：{len(link_lists)}，当前：{link_lists.index(Image_link) + 1} 个，当前链接：{Image_link}")
                time.sleep(0.1)
                # try:
                #     response = requests.get(
                #         Image_link, headers=self.headers, cookies=cookie_file(),
                #         # proxies=mysql_ip_pool()
                #     )
                #     html = response.text
                #     selector = etree.HTML(html)
                #     # 调用提取文本的方法
                #     return_word = Extraction_tools(selector)
                #     if return_word == "获取文本失败":
                #         end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                #         data = {
                #             "链接": Image_link, "时间": end_time, "状态": "采集失败",
                #             "失败原因": return_word
                #         }
                #         log("采集日志", data)  # 写入采集日志
                #     else:
                #         img_src_list = selector.xpath('//*[@id="project-modules"]//img/@src')  # 链接
                #         img_src_list = img_src_list + selector.xpath('//*[@id="project-modules"]//img/@data-src')
                #         # print(img_src_list)  # 打印检查
                #         to_remove = 'https://a5.behance.net'  # 排除a5的链接，a5不是
                #         new_list = [x for x in img_src_list if to_remove not in x]  # 图片的去重
                #         print("成功，准备写入图片")
                #         print(f"图片链接：{new_list}，项目链接：{Image_link}，文字：{return_word}")  # 打印检查
                #         self.write(new_list, Image_link, return_word)
                # except:
                #     # 出现请求失败会将文件写入
                #     fails.append(Image_link)
                #     log('链接请求失败', fails)
                #     end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                #     data = {
                #         "链接": Image_link, "时间": end_time, "状态": "采集失败",
                #         "失败原因": traceback.format_exc()
                #     }
                #     log("采集日志", data)  # 写入采集日志
                #     print(traceback.format_exc())
                #     print(f"当前链接：{Image_link}，请求出现问题，跳过")
                #     time.sleep(1)
                #     pass
                # time.sleep(0.5)
            self.Next(endCursor)

    # 写入图片
    def write(self, new_list, Image_link, return_word):
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
            Storage(folder, folder_1, Image_link, new_list, return_word)  # 写入数据

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


# 启动获取代理ip方法
def run_IpPool():
    ip = IpPool()
    ip.run()


# 启动爬虫方法
def run_ImageSpider():
    ImageSpider_1 = ImageSpider()
    ImageSpider_1.First_page()


if __name__ == '__main__':
    # ImageSpider_1 = ImageSpider()
    # ImageSpider_1.First_page()
    t1 = threading.Thread(target=run_IpPool)
    t2 = threading.Thread(target=run_ImageSpider)
    t1.start()  # 开始线程
    # t2.start()
    t1.join()  # 等待线程结束
    # t2.join()
