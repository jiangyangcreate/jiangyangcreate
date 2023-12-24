import feedparser
import pathlib
from datetime import datetime
import time


class Spider:
    def __init__(self) -> None:
        self.root = pathlib.Path(__file__).parent.resolve()
        self.readme = [self.root / "README.md", self.root / "README_zh.md"]

    def fetch_blog(self):
        content = feedparser.parse("https://jiangmiemie.com/blog/rss.xml")["entries"]

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
        if type == self.root / "README.md":
            return "[Automated by GitHub Actions at UTC {}](build_readme.py)".format(
                now
            )
        elif type == self.root / "README_zh.md":
            return "[由 GitHub Actions 于 {} 自动构建](build_readme.py)".format(now)

    def extract_custom_section(
        self, contents, key="<!-- Automated by GitHub Actions -->\n"
    ):
        for path in self.readme:
            custom_section = path.open("r", encoding="utf-8").read().split(key)[0] + key
            for i in contents:
                custom_section += "\n" + i + "\n"
            custom_section += "\n" + self.fetch_now(path) + "\n"
            path.open("w", encoding="utf-8").write(custom_section)

    def main(self):
        blog = spider.fetch_blog()
        self.extract_custom_section([blog])


if __name__ == "__main__":
    spider = Spider()
    spider.main()
