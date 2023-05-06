import json
import os
import time
import traceback

import requests
from cookie_file import fanye_cookie, fanye_headers
from lxml import etree

with open('../2_0/links.json', 'r') as f:
    links = json.load(f)


class ImageSpider:
    def __init__(self):
        self.headers = {
            "authority": "www.behance.net",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "max-age=0",
            "referer": "https://www.behance.net/",
            "sec-ch-ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        }
        self.cookies = {
            "OptanonAlertBoxClosed": "2024-04-19T02:19:57.109Z",
            "_fbp": "fb.1.1681870800480.1537134479",
            "sign_up_prompt": "true",
            "dialog_dismissals": "announcement_36%3Blogin_prompt",
            "g_state": "{\"i_p\":1681976696030,\"i_l\":2}",
            "bcp": "4afa7c0a-8d01-4c4a-9869-077b92e0e518",
            "bcp_generated": "1681958339302",
            "gki": "{%22feature_adobe_checkout_modal_primary_nav%22:false%2C%22feature_project_gql%22:false%2C%22feature_creative_cloud_search%22:false%2C%22feature_search_shortcuts_mvp%22:false%2C%22feature_gql_profile_drafts_request%22:false%2C%22feature_creative_cloud_card%22:false}",
            "gk_suid": "15734908",
            "originalReferrer": "",
            "iat0": "eyJhbGciOiJSUzI1NiIsIng1dSI6Imltc19uYTEta2V5LWF0LTEuY2VyIiwia2lkIjoiaW1zX25hMS1rZXktYXQtMSIsIml0dCI6ImF0In0.eyJpZCI6IjE2ODE5ODIxNDAzMzFfNTBkZjRlZGMtZTcyOS00MjRlLWJlODMtZDNiNGUxMzAxNzYzX3V3MiIsInR5cGUiOiJhY2Nlc3NfdG9rZW4iLCJjbGllbnRfaWQiOiJCZWhhbmNlV2ViU3VzaTEiLCJ1c2VyX2lkIjoiQzhERDJCQTE2NDNGQTY3MTBBNDk1Q0I0QEFkb2JlSUQiLCJhcyI6Imltcy1uYTEiLCJhYV9pZCI6IkM4REQyQkExNjQzRkE2NzEwQTQ5NUNCNEBBZG9iZUlEIiwiY3RwIjowLCJmZyI6IlhMN09XRzVWVlBONU1QNEtFTVFWWkhRQUJBPT09PT09Iiwic2lkIjoiMTY4MTg5MzQyMzk4NF9lNGI0Y2M2Zi1iNDQyLTQzNmQtOGFiMy0wN2NkNWZiMGViZTJfdXcyIiwibW9pIjoiMzA1YzU2MWEiLCJwYmEiOiJNZWRTZWNOb0VWLExvd1NlYyIsImV4cGlyZXNfaW4iOiI4NjQwMDAwMCIsImNyZWF0ZWRfYXQiOiIxNjgxOTgyMTQwMzMxIiwic2NvcGUiOiJBZG9iZUlELG9wZW5pZCxnbmF2LHNhby5jY2VfcHJpdmF0ZSxjcmVhdGl2ZV9jbG91ZCxjcmVhdGl2ZV9zZGssYmUucHJvMi5leHRlcm5hbF9jbGllbnQsYWRkaXRpb25hbF9pbmZvLnJvbGVzIn0.XqhMFst_vCX8X6bNfVQiyKXSQl2dh44mcK_A8ETOhQQOLGuZdqSbA9--_mZ-nAJWA6WjAP-2DkulL7NJ2378X_PPAdIEgF_ZC7RgQm9-nKmqJ93C2xp-8xTckpxPaBU1d0iB9AQd7do_Es0YMmsIhBooo6ffxEMo6RnNdZGyF0ikTTryHTDgTqbz1jS41MdPZbobu2nYKLozwQydIRfKM82dbz_ULIvMJLJ6O3nfTz_ve55bawD7A7g9frOzTfoCsY7zSaaSJt9RzYEftvYhJ6xtlg9nZqj_i_iy-Rvi5vKYp_eR0ASYsZJv36k-vrleEj8YyuSHyEYCCBOWUHeuOA",
            "gpv": "behance.net:for_you",
            "AMCVS_9E1005A551ED61CA0A490D45%40AdobeOrg": "1",
            "AMCV_9E1005A551ED61CA0A490D45%40AdobeOrg": "870038026%7CMCMID%7C91811164132661141023703059430676136509%7CMCAAMLH-1682586950%7C9%7CMCAAMB-1682586950%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1681989350s%7CNONE%7CMCAID%7CNONE%7CMCCIDH%7C-931107674%7CvVersion%7C5.0.0",
            "s_cc": "true",
            "OptanonConsent": "groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1",
            "s_ppv": "[%22www.behance.net/%22%2C8%2C0%2C714%2C834%2C714%2C1536%2C864%2C1.25%2C%22P%22]"
        }
        self.excludeProjectIds = []

    # 第一页
    def first_request(self):
        # 解析HTML页面
        url = "https://www.behance.net/"
        print("开始第一页")
        response = requests.get(url, headers=self.headers, cookies=self.cookies)
        print(response.text)
        if response.status_code == 200:
            html = etree.HTML(response.text)
            link_list = []
            link_lists = []
            a_list = html.xpath('//a[@title="项目的链接"]')
            for a in a_list:
                href = a.xpath('@href')[0]
                # 检验链接是否存在
                new_link = f"https://www.behance.net{href}"
                if new_link in links:
                    print("链接已存在")
                else:
                    link_list.append(new_link)
                    links.append(new_link)
                    with open('links.json', 'w') as f:
                        json.dump(links, f)
            # 列表推导式，去重
            [link_lists.append(c) for c in link_list if c not in link_lists]
            print(f"返回：{link_lists}")
            return link_lists
        # else:
        #     print("第一次状态码不等于200")
        url = "https://www.behance.net/v3/graphql"
        data = {
            "query": "\n  query getForYouFeed(\n    $excludeProjectIds: [Int]\n    $excludeEntities: [ForYouFeedExcludeEntity!]\n    $extraEntityTypes: [ForYouFeedItemEntityType!] = [USERLIVESTREAM, FOLLOWED_TAG_PROJECT]\n  ) {\n    forYouFeed(\n      first: 48\n      excludeProjectIds: $excludeProjectIds\n      extraEntityTypes: $extraEntityTypes\n      excludeEntities: $excludeEntities\n    ) {\n      nodes {\n        action\n        actor {\n          __typename\n          ... on FollowableTag {\n            tag {\n              id\n              title\n            }\n          }\n        }\n        entity {\n          ... on Project {\n            __typename\n            id\n            name\n            slug\n            url\n            covers {\n              size_202 {\n                url\n              }\n              size_404 {\n                url\n              }\n              size_max_808 {\n                url\n              }\n              size_202_webp {\n                url\n              }\n              size_404_webp {\n                url\n              }\n              size_max_808_webp {\n                url\n              }\n            }\n            colors {\n              r\n              g\n              b\n            }\n            owners {\n              ...OwnerFields\n              images {\n                size_50 {\n                  url\n                }\n              }\n            }\n            linkedAssetsCount\n            linkedAssets {\n              ...sourceLinkFields\n            }\n            sourceFiles {\n              ...sourceFileFields\n            }\n            isPrivate\n            publishedOn\n            premium\n            isFeatured\n            stats {\n              appreciations {\n                all\n              }\n              views {\n                all\n              }\n            }\n            features {\n              featuredOn\n              url\n              name\n              ribbon {\n                image\n                image2x\n              }\n            }\n            isFounder\n            modifiedOn\n            matureAccess\n            hasMatureContent\n            adminFlags {\n              mature_lock\n              privacy_lock\n              dmca_lock\n              flagged_lock\n              privacy_violation_lock\n              trademark_lock\n              spam_lock\n            }\n          }\n          ... on UserLivestream {\n            __typename\n            id\n            title\n            streamId\n            createdOn\n            isPremium\n            animatedThumbnailUrl\n            videoPageUrl\n            linkedAssetsCount\n            linkedAssets {\n              __typename\n              url\n              name\n              premium\n            }\n            thumbnailUrl\n            adminFlags {\n              LIVESTREAM_LOCK\n              NEEDS_REVIEW\n            }\n            privacy\n            status\n            isLive\n            durationSeconds\n            videoPageUrl\n            streamer {\n              id\n              displayName\n              username\n              images {\n                size_50 {\n                  url\n                }\n              }\n            }\n            videoId\n            state\n            tools {\n              title\n              synonym {\n                iconUrl\n              }\n            }\n            views\n          }\n        }\n      }\n    }\n  }\n\n  \n  fragment sourceLinkFields on LinkedAsset {\n    __typename\n    moduleIds\n    name\n    premium\n    url\n    category\n    licenseType\n  }\n\n  \n  fragment sourceFileFields on SourceFile {\n    __typename\n    sourceFileId\n    projectId\n    userId\n    title\n    assetId\n    renditionUrl\n    mimeType\n    size\n    category\n    licenseType\n    moduleIds\n    unitAmount\n    currency\n    tier\n    hidden\n    extension\n    hasUserPurchased\n  }\n\n  \n  fragment OwnerFields on User {\n    displayName\n    hasPremiumAccess\n    id\n    isFollowing\n    isProfileOwner\n    location\n    locationUrl\n    url\n    username\n  }\n\n",
        }
        data = json.dumps(data, separators=(',', ':'))
        response = requests.post(url, headers=fanye_headers(), cookies=fanye_cookie(), data=data)
        print(response.json())
        print("---" * 100)
        link_lists = []
        link_list = []
        excludeEntities_list = []
        for i in response.json()["data"]["forYouFeed"]["nodes"]:
            try:
                self.excludeProjectIds.append(int(i["entity"]['id']))
                excludeEntities_list.append({
                    "entityType": "PROJECT",
                    "entityId": int(i["entity"]['id'])
                })
                # 检验链接是否存在
                new_link = i["entity"]["url"]
                if new_link in links:
                    print("链接已存在")
                else:
                    link_list.append(new_link)
                    links.append(new_link)
                    with open('../2_0/links.json', 'w') as f:
                        json.dump(links, f)
            except:
                print("跳过")
                pass
        [link_lists.append(c) for c in link_list if c not in link_lists]
        self.second_request(link_lists, excludeEntities_list)

    def fanye(self, excludeEntities_list):
        print("开始翻页")
        url = "https://www.behance.net/v3/graphql"
        data = {
            "query": "\n  query getForYouFeed(\n    $excludeProjectIds: [Int]\n    $excludeEntities: [ForYouFeedExcludeEntity!]\n    $extraEntityTypes: [ForYouFeedItemEntityType!] = [USERLIVESTREAM, FOLLOWED_TAG_PROJECT]\n  ) {\n    forYouFeed(\n      first: 48\n      excludeProjectIds: $excludeProjectIds\n      extraEntityTypes: $extraEntityTypes\n      excludeEntities: $excludeEntities\n    ) {\n      nodes {\n        action\n        actor {\n          __typename\n          ... on FollowableTag {\n            tag {\n              id\n              title\n            }\n          }\n        }\n        entity {\n          ... on Project {\n            __typename\n            id\n            name\n            slug\n            url\n            covers {\n              size_202 {\n                url\n              }\n              size_404 {\n                url\n              }\n              size_max_808 {\n                url\n              }\n              size_202_webp {\n                url\n              }\n              size_404_webp {\n                url\n              }\n              size_max_808_webp {\n                url\n              }\n            }\n            colors {\n              r\n              g\n              b\n            }\n            owners {\n              ...OwnerFields\n              images {\n                size_50 {\n                  url\n                }\n              }\n            }\n            linkedAssetsCount\n            linkedAssets {\n              ...sourceLinkFields\n            }\n            sourceFiles {\n              ...sourceFileFields\n            }\n            isPrivate\n            publishedOn\n            premium\n            isFeatured\n            stats {\n              appreciations {\n                all\n              }\n              views {\n                all\n              }\n            }\n            features {\n              featuredOn\n              url\n              name\n              ribbon {\n                image\n                image2x\n              }\n            }\n            isFounder\n            modifiedOn\n            matureAccess\n            hasMatureContent\n            adminFlags {\n              mature_lock\n              privacy_lock\n              dmca_lock\n              flagged_lock\n              privacy_violation_lock\n              trademark_lock\n              spam_lock\n            }\n          }\n          ... on UserLivestream {\n            __typename\n            id\n            title\n            streamId\n            createdOn\n            isPremium\n            animatedThumbnailUrl\n            videoPageUrl\n            linkedAssetsCount\n            linkedAssets {\n              __typename\n              url\n              name\n              premium\n            }\n            thumbnailUrl\n            adminFlags {\n              LIVESTREAM_LOCK\n              NEEDS_REVIEW\n            }\n            privacy\n            status\n            isLive\n            durationSeconds\n            videoPageUrl\n            streamer {\n              id\n              displayName\n              username\n              images {\n                size_50 {\n                  url\n                }\n              }\n            }\n            videoId\n            state\n            tools {\n              title\n              synonym {\n                iconUrl\n              }\n            }\n            views\n          }\n        }\n      }\n    }\n  }\n\n  \n  fragment sourceLinkFields on LinkedAsset {\n    __typename\n    moduleIds\n    name\n    premium\n    url\n    category\n    licenseType\n  }\n\n  \n  fragment sourceFileFields on SourceFile {\n    __typename\n    sourceFileId\n    projectId\n    userId\n    title\n    assetId\n    renditionUrl\n    mimeType\n    size\n    category\n    licenseType\n    moduleIds\n    unitAmount\n    currency\n    tier\n    hidden\n    extension\n    hasUserPurchased\n  }\n\n  \n  fragment OwnerFields on User {\n    displayName\n    hasPremiumAccess\n    id\n    isFollowing\n    isProfileOwner\n    location\n    locationUrl\n    url\n    username\n  }\n\n",
            "variables": {
                "excludeProjectIds": self.excludeProjectIds,
                "excludeEntities": excludeEntities_list,
                "extraEntityTypes": [
                    "USERLIVESTREAM",
                    "FOLLOWED_TAG_PROJECT"
                ]
            }
        }
        data = json.dumps(data, separators=(',', ':'))
        response = requests.post(url, headers=fanye_headers(), cookies=fanye_cookie(), data=data)
        print(response.json())
        link_lists = []
        link_list = []
        excludeEntities_list = []
        for i in response.json()["data"]["forYouFeed"]["nodes"]:
            try:
                self.excludeProjectIds.append(int(i["entity"]['id']))
                excludeEntities_list.append({
                    "entityType": "PROJECT",
                    "entityId": int(i["entity"]['id'])
                })
                # 检验链接是否存在
                new_link = i["entity"]["url"]
                if new_link in links:
                    print("链接已存在")
                else:
                    link_list.append(new_link)
                    links.append(new_link)
                    with open('../2_0/links.json', 'w') as f:
                        json.dump(links, f)
            except:
                print("跳过")
                pass
        [link_lists.append(c) for c in link_list if c not in link_lists]
        print(link_lists)
        self.second_request(link_lists, excludeEntities_list)

    # 对每个详细页的数据进行爬取
    def second_request(self, link_lists, excludeEntities_list):
        if len(link_lists) == 0:
            print("link_lists列表为空，停止")
        else:
            for Image_link in link_lists:
                print(f"共计：{len(link_lists)}，当前：{link_lists.index(Image_link) + 1} 个，当前链接：{Image_link}")
                try:
                    response = requests.get(Image_link, headers=self.headers, cookies=self.cookies, timeout=15)
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
                    print(traceback.format_exc())
                    print(f"当前链接：{Image_link}，请求出现问题，跳过")
                    pass
                time.sleep(0.5)
            try:
                self.fanye(excludeEntities_list)
            except:
                print("翻页出现问题")

    def write(self, folders, link):
        # 创建文件夹不能有/ |
        folder = folders.replace(" ", "_").replace("/", "_").replace("|", "_")
        if not os.path.exists(folder):
            os.mkdir(folder)
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        }
        for image_url in link:
            print(f"{link.index(image_url)}：正在写入...")
            try:
                r = requests.get(image_url, headers=headers, timeout=15)
                down_time = int(time.time() * 1000)
                with open(f"{folder}/{down_time}.jpg", mode="wb") as f:
                    f.write(r.content)
            except:
                print("图片请求超时...跳过")
                pass
        print(f"{folder}，所有图片写入成功")


if __name__ == '__main__':
    ImageSpider = ImageSpider()
    ImageSpider.first_request()
