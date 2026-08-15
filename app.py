from bs4 import BeautifulSoup
from ddgs import DDGS
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
      # Փորձում ենք առաջին հարցումը
      query = f"{name} անվան նշանակությունը բացատրություն"
      url = None

      try:
        with DDGS() as ddgs:
          results = list(ddgs.text(query, region="am-hy", max_results=5))

          # Եթե հայերեն տարածաշրջանով չգտավ, փորձենք առանց տարածաշրջանի սահմանափակման
          if not results:
            results = list(ddgs.text(query, max_results=5))

          # Եթե էլի չգտավ, փորձենք ավելի պարզ հարցում (միայն անունը)
          if not results:
            results = list(ddgs.text(name, max_results=5))

          for r in results:
            link = r.get("href", "")
            if "wikipedia.org" not in link:
              url = link
              break
          if not url and results:
            url = results[0].get("href")

          source_url = url
      except Exception:
        pass

      # Եթե հղում գտնվեց, փորձում ենք կարդալ
      if source_url:
        try:
          headers = {
              "User-Agent": (
                  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                  " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
              ),
              "Accept-Language": "hy,en-US;q=0.9,en;q=0.8",
          }
          response = requests.get(source_url, headers=headers, timeout=10)
          response.encoding = response.apparent_encoding
          soup = BeautifulSoup(response.text, "html.parser")

          paragraphs = soup.find_all("p")
          text_list = [
              p.get_text().strip()
              for p in paragraphs
              if len(p.get_text().strip()) > 20
          ]

          if text_list:
            meaning = "\n\n".join(text_list[:3])
          else:
            meaning = (
                "Ցավոք, գտնված էջից հնարավոր չեղավ տեքստ առանձնացնել:"
            )
        except Exception:
          meaning = "Տվյալները կարդալիս սխալ առաջացավ:"
      else:
        meaning = (
            f"Ցավոք, «{name}» անվան վերաբերյալ տեղեկություն կամ կայքէջ չգտնվեց:"
        )

  return render_template(
      "index.html", meaning=meaning, name=name, source_url=source_url
  )


if __name__ == "__main__":
  app.run(debug=True)
