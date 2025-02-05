import os
import json
import time
import hashlib
import pathlib
import requests
import feedparser
from parsel import Selector
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import re
from openai import OpenAI

class LLM:
    @staticmethod
    def hide_think_output(show_think=True):
        def decorator(func):
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                if not show_think:

                    result = re.sub(r"<think>.*?</think>", "", result, flags=re.DOTALL)
                return result

            return wrapper

        return decorator

    @hide_think_output(show_think=False)
    @staticmethod
    def get_result(text: str):
        DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

        assert DASHSCOPE_API_KEY is not None, "DASHSCOPE_API_KEY is not set"

        client = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            api_key=DASHSCOPE_API_KEY,  # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        completion = client.chat.completions.create(
            model="deepseek-v3",
            messages=[
                {
                    "role": "user",
                    "content": "阅读下面的博文，然后尽可能接近50个词的范围内，提供一个总结。只需要回复总结后的文本：{}".format(
                        text
                    ),
                }
            ],
        )
        return completion.choices[0].message.content

class Jsonsummary:
    def __init__(self):
        root = pathlib.Path(__file__).parent.resolve()
        self.json_file_path = os.path.join(root, "summary")
        self.url = "https://jiangmiemie.com/"
        self.pages = []

    def load_json(self):
        # 加载JSON文件
        loaded_dict = {}
        for file in os.listdir(self.json_file_path):
            with open(
                os.path.join(self.json_file_path, file), "r", encoding="utf-8"
            ) as json_file:
                loaded_dict[self.url + file.replace("_", "/").replace(".json", "")] = (
                    json.load(json_file)
                )
        return loaded_dict

    def save_json(self, loaded_dict):
        # 将字典存入JSON文件
        for key in loaded_dict:
            key_path = key.replace(self.url, "").replace("/", "_") + ".json"
            save_path = os.path.join(self.json_file_path, key_path)
            with open(save_path, "w", encoding="utf-8") as json_file:
                json.dump(loaded_dict[key], json_file, indent=4)

    def clean_json(self):
        # 根据RSS结果清理JSON文件
        for file in os.listdir(self.json_file_path):
            if file not in self.pages:
                os.remove(os.path.join(self.json_file_path, file))


def blog_summary(feed_content):
    jsdata = Jsonsummary()
    loaded_dict = jsdata.load_json()

    for page in feed_content:
        url = page["link"].split("#")[0]
        jsdata.pages.append(url.replace(jsdata.url, "").replace("/", "_") + ".json")
        # 剪切掉摘要部分，仅保留正文
        content = "".join(
            page["content"][0]["value"].split(
                "此内容根据文章生成，仅用于文章内容的解释与总结"
            )[1:]
        )
        selector = Selector(text=content)
        content_format = "".join(selector.xpath(".//text()").getall())
        content_hash = hashlib.md5(content_format.encode()).hexdigest()
        if (
            loaded_dict.get(url)
            and loaded_dict.get(url).get("content_hash") == content_hash
        ):
            continue
        else:
            summary = LLM.get_result(content_format)
            loaded_dict.update(
                {url: {"content_hash": content_hash, "summary": summary}}
            )

    jsdata.save_json(loaded_dict)
    jsdata.clean_json()


class Readme:
    def __init__(self, path) -> None:
        self.root = pathlib.Path(__file__).parent.resolve()
        self.file_path = self.root / "{}.md".format(path)

        self.jinja = Environment(
            loader=FileSystemLoader(os.path.join(self.root, "jinja"))
        ).get_template("{}.jinja".format(path))


class Spider:
    def __init__(self) -> None:

        self.readme = [Readme("README"), Readme("README_zh")]

    def fetch_weather(self, city="shenzhen"):
        url = "https://wttr.in/{}?m&format=3".format(city)
        try:
            res = requests.get(url).text.split(":")[1].replace("\n", "")
        except:
            res = "⛅️  0°C"
        return res

    def fetch_blog(self):
        content = feedparser.parse("https://jiangmiemie.com/blog/rss.xml")["entries"]
        blog_summary(content)
        entries = [
            "* <a href='{url}' target='_blank'>{title}</a> - {published}".format(
                title=entry["title"],
                url=entry["link"].split("#")[0],
                published=datetime.strptime(
                    entry["published"], "%a, %d %b %Y %H:%M:%S %Z"
                ).strftime("%Y-%m-%d"),
            )
            for entry in content
        ]

        return "\n".join(entries[:5])

    def fetch_now(self, type):
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if str(type).endswith("README.md"):
            return "[Automated by GitHub Actions at UTC {}](build_readme.py)".format(
                now
            )
        elif str(type).endswith("README_zh.md"):
            return "[由 GitHub Actions 于 UTC {} 自动构建](build_readme.py)".format(now)

    def main(self):
        weather = spider.fetch_weather()
        blog = spider.fetch_blog()
        for i in self.readme:
            file_path = i.file_path
            jinja = i.jinja
            fetch = spider.fetch_now(file_path)
            context = {
                "weather": weather,
                "fetch": fetch,
                "blog": blog,
            }
            custom_section = jinja.render(context)
            file_path.open("w", encoding="utf-8").write(custom_section)


if __name__ == "__main__":
    spider = Spider()
    spider.main()
