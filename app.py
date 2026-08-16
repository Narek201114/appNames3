from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from flask import Flask, render_template, request
import requests
app = Flask(__name__)


def is_armenian(text):
  armenian_letters = set("աբգդեզէըթժիլխծկհձղճմյնշոչպջռսվտրցւփքօֆև")
  return any(char in armenian_letters for char in text.lower())


@app.route("/", methods=["GET", "POST"])
def index():
  meaning = None
  name = None
  source_url = None

  if request.method == "POST":
    name = request.form.get("name", "").strip()
    if name:
      query = f"{name} անվան նշանակությունը ի՞նչ է նշանակում"
      urls_to_try = []

      try:
        with DDGS() as ddgs:
          results = list(ddgs.text(query, region="am-hy", max_results=10))
          if not results:
            results = list(ddgs.text(query, max_results=10))

          for r in results:
            link = r.get("href", "")
            if (
                link
                and "wikipedia.org" not in link
                and "facebook.com" not in link
                and "youtube.com" not in link
            ):
              urls_to_try.append(link)
      except Exception:
        pass

      headers = {
          "User-Agent": (
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
              " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
          ),
          "Accept-Language": "hy,en-US;q=0.9,en;q=0.8",
      }

      for u in urls_to_try:
        try:
          response = requests.get(u, headers=headers, timeout=6)
          if response.status_code == 200:
            response.encoding = response.apparent_encoding
            soup = BeautifulSoup(response.text, "html.parser")

            paragraphs = soup.find_all("p")
            text_list = []
            for p in paragraphs:
              txt = p.get_text().strip()
              if (
                  len(txt) > 60
                  and is_armenian(txt)
                  and "Բիզնես" not in txt
                  and "Գործարար" not in txt
                  and "Cookie" not in txt
                  and "Կայքի" not in txt
              ):
                text_list.append(txt)

            if text_list:
              source_url = u
              meaning = text_list[0]
              break
        except Exception:
          continue

      if not meaning and urls_to_try:
        source_url = urls_to_try[0]
        meaning = (
            "Ավտոմատ կերպով տեքստը հնարավոր չեղավ կարդալ: Խնդրում ենք սեղմել"
            " ստորև բերված հղումը:"
        )
      elif not meaning:
        meaning = f"Ցավոք, «{name}» անվան վերաբերյալ տեղեկություն չգտնվեց:"

  return render_template(
      "index.html", meaning=meaning, name=name, source_url=source_url
  )


if __name__ == "__main__":
  app.run(debug=True)
