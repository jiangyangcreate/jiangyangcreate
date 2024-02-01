import feedparser
import pathlib
from datetime import datetime
import time
import requests
import summary
from jinja2 import Environment, FileSystemLoader

class Readme:
    def __init__(self, path) -> None:
        self.root = pathlib.Path(__file__).parent.resolve()
        self.file_path = self.root / path.replace(".jinja", ".md")
        self.jinja = Environment(loader=FileSystemLoader(self.root)).get_template(path)
class Spider:
    def __init__(self) -> None:
        
        self.readme = [Readme("README.jinja"), Readme("README_zh.jinja")]

    def fetch_weather(self, city="shenzhen"):
        url = "https://wttr.in/{}?m&format=3".format(city)
        try:
            res = requests.get(url).text.split(":")[1].replace('\n', '')
        except:
            res = "⛅️  0°C"
        return res

    def fetch_blog(self):
        content = feedparser.parse("https://jiangmiemie.com/blog/rss.xml")["entries"]
        summary.summary(content)
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
                "weather" : weather,
                "fetch" : fetch,
                "blog" : blog,
                }
            custom_section = jinja.render(context)
            file_path.open("w", encoding="utf-8").write(custom_section)


if __name__ == "__main__":
    spider = Spider()
    spider.main()
