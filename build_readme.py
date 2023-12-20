import feedparser
import pathlib
from datetime import datetime


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

    def extract_custom_section(
        self, content, key="<!-- Automated by GitHub Actions -->\n"
    ):
        for path in self.readme:
            custom_section = path.open("r", encoding="utf-8").read().split(key)[0]
            content = custom_section + key + content
            path.open("w", encoding="utf-8").write(content)

    def main(self):
        blog = spider.fetch_blog()
        self.extract_custom_section(blog)


if __name__ == "__main__":
    spider = Spider()
    spider.main()
