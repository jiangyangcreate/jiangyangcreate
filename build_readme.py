import feedparser
import pathlib
from datetime import datetime
import time


class Spider:
    def __init__(self) -> None:
        self.root = pathlib.Path(__file__).parent.resolve()
        self.readme = [
            self.root / "README.md",
            # self.root / "README_cn.md"
        ]

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

    def fetch_now(self):
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return "[Automated by GitHub Actions at UTC {}](build_readme.py)".format(now)

    def extract_custom_section(
        self, contents, key="<!-- Automated by GitHub Actions -->\n"
    ):
        for path in self.readme:
            custom_section = path.open("r", encoding="utf-8").read().split(key)[0] + key
            for i in contents:
                custom_section += "\n" + i + "\n"
            path.open("w", encoding="utf-8").write(custom_section)

    def main(self):
        blog = spider.fetch_blog()
        now = self.fetch_now()
        self.extract_custom_section([blog, now])


if __name__ == "__main__":
    spider = Spider()
    spider.main()
