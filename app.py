from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from flask import Flask, render_template, request
import requests

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
  meaning = None
  name = None
  source_url = None

  if request.method == "POST":
    name = request.form.get("name", "").strip()
    if name:
      query = f"{name} անվան նշանակությունը բացատրություն"

      headers = {
          "User-Agent": (
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
              " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
          ),
          "Accept-Language": "hy,en-US;q=0.9,en;q=0.8",
      }

      url = None
      try:
        # Որոնում ենք DuckDuckGo-ի միջոցով
        with DDGS() as ddgs:
          results = list(ddgs.text(query, region="am-hy", max_results=5))
          if not results:
            results = list(ddgs.text(query, max_results=5))

          if results:
            # Խուսափում ենք wikipedia.org-ից, եթե հնարավոր է
            for r in results:
              link = r.get("href", "")
              if "wikipedia.org" not in link:
                url = link
                break

            # Եթե բոլորը Վիքիպեդիա էին, վերցնում ենք առաջինը
            if not url and results:
              url = results[0].get("href", "")
      except Exception as e:
        print(f"Որոնման սխալ՝ {e}")

      # Եթե հղումը գտնվել է, փորձում ենք կարդալ տեքստը
      if url:
        source_url = url
        try:
          response = requests.get(url, headers=headers, timeout=8)
          response.encoding = response.apparent_encoding
          soup = BeautifulSoup(response.text, "html.parser")

          paragraphs = soup.find_all("p")
          text_list = [
              p.get_text().strip()
              for p in paragraphs
              if len(p.get_text().strip()) > 30
          ]

          if text_list:
            meaning = "\n\n".join(text_list[:3])
          else:
            meaning = (
                f"«{name}» անվան մասին տեղեկություն գտնվեց, սակայն էջից"
                " հնարավոր չեղավ տեքստ առանձնացնել:"
            )
        except Exception as e:
          meaning = f"Տեղեկությունը կարդալու ընթացքում սխալ առաջացավ։"
      else:
        meaning = f"Ցավոք, «{name}» անվան վերաբերյալ որեւէ բան չգտնվեց:"

  return render_template(
      "index.html", meaning=meaning, name=name, source_url=source_url
  )


if __name__ == "__main__":
  app.run(debug=True)
