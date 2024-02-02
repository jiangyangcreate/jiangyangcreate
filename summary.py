import os
import json
import requests
from parsel import Selector


class BaiduAI:
    def __init__(self):
        self.BAIDU_API_KEY = os.getenv("BAIDU_API_KEY")
        self.BAIDU_SECRET_KEY = os.getenv("BAIDU_SECRET_KEY")
        self.token = self.get_access_token()

    def get_access_token(self):
        """
        :return: access_token
        """
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.BAIDU_API_KEY,
            "client_secret": self.BAIDU_SECRET_KEY,
        }
        return str(requests.post(url, params=params).json().get("access_token"))

    def get_result(self, text: str):
        messages = json.dumps(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "阅读下面的博文，然后尽可能接近50个词的范围内，提供一个总结。只需要回复总结后的文本：{}".format(
                            text
                        ),
                    }
                ]
            }
        )
        session = requests.request(
            "POST",
            "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token="
            + self.token,
            headers={"Content-Type": "application/json"},
            data=messages,
        )
        json_data = json.loads(session.text)
        if "result" in json_data.keys():
            answer_text = json_data["result"]
        return answer_text


def get_summary(content: str) -> str:
    # 剪切掉摘要部分，仅保留正文
    selector = Selector(text=content.split('此内容根据文章生成，仅用于文章内容的解释与总结')[1])
    content_format = "".join(selector.xpath(".//text()").getall())
    ai = BaiduAI()
    summary = ai.get_result(content_format)
    return summary


def summary(feed_content):
    json_file_path = "output.json"

    # 如果JSON文件不存在，则创建一个空的JSON文件
    if not os.path.exists(json_file_path):
        with open(json_file_path, "w", encoding="utf-8") as new_json_file:
            json.dump({}, new_json_file)

    # 读取JSON文件并将其转换为Python字典
    with open(json_file_path, "r", encoding="utf-8") as json_file:
        loaded_dict = json.load(json_file)

    for page in feed_content:
        url = page["link"].split("#")[0]
        content = page["content"][0]["value"]
        content_hash = hash(content)
        if (
            loaded_dict.get(url)
            and loaded_dict.get(url).get("content_hash") == content_hash
        ):
            continue
        else:
            summary = get_summary(content)
            loaded_dict.update({url: {'content_hash': content_hash, 'summary': summary}})
    # 将字典存入JSON文件
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(loaded_dict, json_file, indent=4)
