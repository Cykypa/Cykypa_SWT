import json
import re

import requests

from 图片采集4_0.config import country_data_dict_list

headers = {
    "authority": "www.behance.net",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "cache-control": "max-age=0",
    "sec-ch-ua": "\"Chromium\";v=\"112\", \"Microsoft Edge\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.68"
}
cookies = {
    "OptanonAlertBoxClosed": "2024-04-19T02:53:52.257Z",
    "OptanonConsent": "groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1",
    "dialog_dismissals": "announcement_36%3Blogin_prompt",
    "sign_up_prompt": "true",
    "gki": "{%22feature_adobe_checkout_modal_primary_nav%22:false%2C%22feature_creative_cloud_search%22:false%2C%22feature_gql_profile_drafts_request%22:false%2C%22feature_inbox_file_uploads%22:false}",
    "AMCV_9E1005A551ED61CA0A490D45%40AdobeOrg": "870038026%7CMCMID%7C19164445593973786131767815682217063165%7CMCAID%7CNONE%7CMCOPTOUT-1683277804s%7CNONE%7CvVersion%7C5.0.0",
    "gk_suid": "29516305",
    "originalReferrer": "",
    "ilo0": "true",
    "bcp": "05807658-7637-4841-a422-b6b66de68002"
}
url = "https://www.behance.net/hire"

data_len = country_data_dict_list()

data = []
data_file = []

with open('./创作者总共数量.json', 'r') as f:
    fails = json.load(f)


def get_total_():
    for country in data_len[13:]:
        print(f"当前是：{data_len.index(country) + 1} 个，共计：{len(data_len)}")
        print(country)
        params = {
            "country": f"{country['value']}"
        }
        response = requests.get(url, headers=headers, cookies=cookies, params=params)
        if response.status_code == 200:
            Html = response.text

            match = re.search(r'"totalSearchCount":(\d+),', Html)
            if match:
                total_search_count = match.group(1)
                # print(total_search_count)
                data.append({f"{country['label']}": total_search_count})
                # print(data)
                fails.append({f"{country['label']}": total_search_count})
                with open('./创作者总共数量.json', 'w') as f:
                    json.dump(fails, f)
                print(f"{country['value']} 成功获取")
                # time.sleep(random.randint(1, 3))
            else:
                print(f"{country['label']} 状态码不正确")
                data_file.append(country)


def quantity():
    total = 0
    for i in fails:
        total = total + int(i[data_len[fails.index(i)]['label']])
    print(total)


if __name__ == '__main__':
    # print(fails)
    # print(len(fails))
    # get_total_()
    # print(data)
    # print(
    #     len(data)
    # )
    # print(data_file)
    quantity()
