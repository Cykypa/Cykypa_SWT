import json


def cookie_file():
    with open('./config/config.json') as f:
        data_json = json.loads(f.read())
    # print(data_json['cookie_file']['cookies']) # 打印检查
    f.close()
    return data_json['cookie_file']['cookies']


# 下一页的headers和cookies
def Next_cookie():
    with open('./config/config.json') as f:
        data_json = json.loads(f.read())
    f.close()
    headers = data_json['Next_cookie']['headers']
    cookies = data_json['Next_cookie']['cookies']
    print(headers, cookies)  # 打印检查
    return {"Next_headers": headers, "Next_cookies": cookies}


if __name__ == '__main__':
    Next_cookie()
