import csv
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://www.musashino-u.ac.jp"
DOMAIN = urlparse(BASE_URL).netloc

# 収集データを格納する辞書 {URL: タイトル}
sitemap_data = {}

# 巡回管理用
visited_urls = set()
urls_to_visit = [BASE_URL]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

print("スクレイピングを開始します...")

while urls_to_visit:
    current_url = urls_to_visit.pop(0)

    if current_url in visited_urls:
        continue

    visited_urls.add(current_url)
    print(f"取得中: {current_url}")

    # サーバー負荷軽減のため必ず1秒待機
    time.sleep(1)

    try:
        res = requests.get(current_url, headers=headers, timeout=10)
        if res.status_code != 200:
            continue

        soup = BeautifulSoup(res.content, "html.parser")

        # <title>タグの文字列を取得
        title = (
            soup.title.string.strip()
            if soup.title and soup.title.string
            else "No Title"
        )
        sitemap_data[current_url] = title

        # ページ内のリンクを辿る
        for a_tag in soup.find_all("a", href=True):
            link = urljoin(BASE_URL, a_tag["href"])
            parsed_link = urlparse(link)

            # 同一ドメインのURLのみ対象
            if parsed_link.netloc == DOMAIN and parsed_link.scheme in [
                "http",
                "https",
            ]:
                clean_link = link.split("#")[0]
                if (
                    clean_link not in visited_urls
                    and clean_link not in urls_to_visit
                ):
                    urls_to_visit.append(clean_link)

    except Exception as e:
        print(f"エラー ({current_url}): {e}")

# CSVファイルに保存
csv_filename = "sitemap.csv"
with open(csv_filename, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["URL", "Title"])
    for url, title in sitemap_data.items():
        writer.writerow([url, title])

print(f"完了！ '{csv_filename}' に出力されました。")