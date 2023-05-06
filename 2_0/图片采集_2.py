import json
import os
import time
import traceback

import requests
from lxml import etree
from sqlalchemy import func

with open('fail.json', 'r') as f:
    fails = json.load(f)

from database import ImageSpiderIp1, DBSession


def mysql_ip_pool():
    session = DBSession()
    random_data = session.query(ImageSpiderIp1).order_by(func.rand()).limit(1).first()
    session.close()
    random_data_list = random_data.ip.split(":")
    proxyMeta = "http://4a565f:c3b53d78@%(host)s:%(port)s" % {  # 账密验证
        "host": random_data_list[0],
        "port": random_data_list[1],
    }
    print("代理1：", proxyMeta)
    proxysdata = {
        'http': proxyMeta,
        'https': proxyMeta
    }
    return proxysdata


class ImageSpider:
    def __init__(self):
        self.headers = {
            "authority": "www.behance.net",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "max-age=0",
            "if-modified-since": "Fri, 21 Apr 2023 08:19:47 +0000",
            "sec-ch-ua": "\"Chromium\";v=\"112\", \"Microsoft Edge\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48"
        }

        self.cookies = {
            "OptanonAlertBoxClosed": "2024-04-19T02:19:57.109Z",
            "_fbp": "fb.1.1681870800480.1537134479",
            "sign_up_prompt": "true",
            "dialog_dismissals": "announcement_36%3Blogin_prompt",
            "g_state": "{\"i_p\":1681976696030,\"i_l\":2}",
            "OptanonConsent": "groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1",
            "bein": "1",
            "gki": "{%22feature_adobe_checkout_modal_primary_nav%22:false%2C%22feature_project_gql%22:false%2C%22feature_creative_cloud_search%22:false%2C%22feature_search_shortcuts_mvp%22:false%2C%22feature_gql_profile_drafts_request%22:false%2C%22feature_creative_cloud_card%22:false}",
            "iat0": "eyJhbGciOiJSUzI1NiIsIng1dSI6Imltc19uYTEta2V5LWF0LTEuY2VyIiwia2lkIjoiaW1zX25hMS1rZXktYXQtMSIsIml0dCI6ImF0In0.eyJpZCI6IjE2ODIzMDY4NzU3NzdfZWM4NWU2YzgtMWJiYy00YTAxLWFlOWEtNjhlMTI2YjhkMjExX3V3MiIsInR5cGUiOiJhY2Nlc3NfdG9rZW4iLCJjbGllbnRfaWQiOiJCZWhhbmNlV2ViU3VzaTEiLCJ1c2VyX2lkIjoiQzhERDJCQTE2NDNGQTY3MTBBNDk1Q0I0QEFkb2JlSUQiLCJhcyI6Imltcy1uYTEiLCJhYV9pZCI6IkM4REQyQkExNjQzRkE2NzEwQTQ5NUNCNEBBZG9iZUlEIiwiY3RwIjowLCJmZyI6IlhNS0E2UFZCVlBONU1QNEtFTVFWWkhRQUJBPT09PT09Iiwic2lkIjoiMTY4MTg5MzQyMzk4NF9lNGI0Y2M2Zi1iNDQyLTQzNmQtOGFiMy0wN2NkNWZiMGViZTJfdXcyIiwibW9pIjoiYWRhNjkyOGMiLCJwYmEiOiJNZWRTZWNOb0VWLExvd1NlYyIsImV4cGlyZXNfaW4iOiI4NjQwMDAwMCIsInNjb3BlIjoiQWRvYmVJRCxvcGVuaWQsZ25hdixzYW8uY2NlX3ByaXZhdGUsY3JlYXRpdmVfY2xvdWQsY3JlYXRpdmVfc2RrLGJlLnBybzIuZXh0ZXJuYWxfY2xpZW50LGFkZGl0aW9uYWxfaW5mby5yb2xlcyIsImNyZWF0ZWRfYXQiOiIxNjgyMzA2ODc1Nzc3In0.c1a2tkHOQ6Kd7-gExuRDsA2tRCMRDp2RgaSUSI6HEzU1JNeSpiogh6WjHIU3DomCnkqPHuJ8zhPruB_idXfla5ajiLjvYs3HhdQEOiwrgHaowmqAlvu6O56ByjC0_tkrUCTVbpUNlinPZmUhx3I4tiyN3mm9MroY4kQtZWPDsXsrrbtmSJuK6OWFc91fZggS9Z84ETPqiqpy0nGRyrr-dz3-qAuav0v2SiKs6-yh75EmYBHvJE_4jEaCNAe1vAkAQ4LVEzvjdmXCt1TupX3TnOtExWw67PbLei8BdhF8UWidnBHM9DHaEKlOaCBID_M5v2flgHCI7l2X6dd-SEAMxw",
            "bcp": "64082816-c0da-4622-935f-f2b390b72ca1",
            "bcp_generated": "1682306880246",
            "gpv": "behance.net:search:projects",
            "AMCV_9E1005A551ED61CA0A490D45%40AdobeOrg": "870038026%7CMCMID%7C91811164132661141023703059430676136509%7CMCAAMLH-1682912728%7C11%7CMCAAMB-1682912728%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1682315128s%7CNONE%7CMCAID%7CNONE%7CMCCIDH%7C-931107674%7CvVersion%7C5.0.0"
        }

    # 对每个详细页的数据进行爬取
    def second_request(self, link_lists):
        if len(link_lists) == 0:
            print("link_lists列表为空，停止")
        else:
            for Image_link in link_lists:
                print(f"共计：{len(link_lists)}，当前：{link_lists.index(Image_link) + 1} 个，当前链接：{Image_link}")
                try:
                    response = requests.get(
                        Image_link, headers=self.headers, cookies=self.cookies, proxies=mysql_ip_pool()
                    )
                    html = response.text
                    selector = etree.HTML(html)
                    title = selector.xpath(  # 标题
                        'normalize-space(//*[@id="site-content"]/div/div[1]/div/div[2]/div[1]/figcaption/span/text())'
                    )
                    img_src_list = selector.xpath('//*[@id="project-modules"]//img/@src')  # 链接
                    to_remove = 'https://a5.behance.net'  # 排除a5的链接，a5不是
                    new_list = [x for x in img_src_list if to_remove not in x]  # 图片的去重
                    print("成功，准备写入图片")
                    self.write(title, new_list)
                except:
                    # 出现请求失败会将文件写入
                    fails.append(Image_link)
                    with open('fail.json', 'w') as f:
                        json.dump(fails, f)
                    print(traceback.format_exc())
                    print(f"当前链接：{Image_link}，请求出现问题，跳过")
                    pass
                time.sleep(0.5)

    def write(self, folders, link):
        # 创建文件夹不能有/ |
        folder = folders.replace(" ", "_").replace("/", "_").replace("|", "_")
        if not os.path.exists(folder):
            os.mkdir(folder)
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        }
        for image_url in link:
            print(f"{link.index(image_url) + 1}：正在写入...")
            try:
                r = requests.get(image_url, headers=headers, timeout=15, proxies=mysql_ip_pool())
                down_time = int(time.time() * 1000)
                with open(f"{folder}/{down_time}.jpg", mode="wb") as f:
                    f.write(r.content)
            except:
                print("图片请求超时...跳过")
                pass
        print(f"{folder}，所有图片写入成功")


if __name__ == '__main__':
    with open('links.json', 'r') as f:
        links = json.load(f)
    links_list = links
    ImageSpider = ImageSpider()
    ImageSpider.second_request(links_list)
