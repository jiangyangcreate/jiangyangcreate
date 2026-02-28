import time
import pathlib
import requests
import feedparser
from jinja2 import Environment, FileSystemLoader

RSS = "https://jiangmiemie.com/blog/rss.xml"
ROOT = pathlib.Path(__file__).parent.resolve()
JINJA_DIR = ROOT / "jinja"
TEMPLATES = ("README", "README_zh")

jinja_env = Environment(loader=FileSystemLoader(JINJA_DIR))


def fetch_blog(page_num: int = 5) -> str:
    entries = feedparser.parse(RSS)["entries"][:page_num]
    lines = []
    for entry in entries:
        title = entry["title"]
        url = entry["link"].split("#")[0]
        published = time.strftime("%Y-%m-%d", entry["published_parsed"])
        lines.append(f"* <a href='{url}' target='_blank'>{title}</a> - {published}")
    return "\n".join(lines)


def fetch_weather(city: str = "shenzhen", timeout: int = 5) -> str:
    try:
        raw = requests.get(
            f"https://wttr.in/{city}?m&format=3", timeout=timeout
        ).text
        return raw.split(":", 1)[1].replace("\n", "").strip()
    except Exception:
        return "⛅️  0°C"


def build_readmes() -> None:
    context = {
        "weather": fetch_weather(),
        "blog": fetch_blog(),
        "fetch": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
    }
    for name in TEMPLATES:
        content = jinja_env.get_template(f"{name}.jinja").render(context)
        output = ROOT / f"{name}.md"
        output.write_text(content, encoding="utf-8")

if __name__ == "__main__":
    build_readmes()
