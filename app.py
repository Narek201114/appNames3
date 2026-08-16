from bs4 import BeautifulSoup
from flask import Flask, render_template, request
import requests

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
  meaning = None
  name = None

  if request.method == "POST":
    name = request.form.get("name", "").strip()
    if name:
      try:
        # Օգտագործում ենք DuckDuckGo-ի հանրային HTML որոնումը (առանց գրադարանների սխալների)
        query = f"{name} անվան նշանակություն"
        search_url = f"https://html.duckduckgo.com/html/?q={query}"

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }

        response = requests.get(search_url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        # Գտնում ենք որոնման առաջին հղումը
        first_link = None
        for a in soup.find_all("a", class_="result__url", href=True):
          first_link = a["href"]
          break

        if not first_link:
          # Այլընտրանքային որոնում հղումների համար
          for a in soup.find_all("a", class_="result__snippet", href=True):
            pass
          # Վերցնում ենք առաջին իսկ արդյունքի տեքստը կամ հղումը
          for a in soup.find_all("a", href=True):
            if "uddg=" in a["href"]:
              # Քաղում ենք իրական հղումը DuckDuckGo-ի միջանկյալ հղումից
              from urllib.parse import parse_qs, urlparse

              parsed_url = urlparse(a["href"])
              captured_url = parse_qs(parsed_url.query).get("uddg")
              if captured_url:
                first_link = captured_url[0]
                break

        # Եթե գտանք հղում, մտնում ենք կարդալու
        if first_link:
          res = requests.get(first_link, headers=headers, timeout=5)
          page_soup = BeautifulSoup(res.text, "html.parser")
          paragraphs = page_soup.find_all("p")

          texts = [
              p.get_text().strip()
              for p in paragraphs
              if len(p.get_text().strip()) > 40
          ]
          if texts:
            meaning = "\n\n".join(texts[:2])
          else:
            meaning = (
                f"«{name}» անվան մասին տեղեկություն գտնվեց ստորև նշված"
                " աղբյուրում:"
            )
        else:
          meaning = f"Ցավոք, «{name}» անվան վերաբերյալ տեղեկություն չգտնվեց:"

      except Exception as e:
        meaning = (
            "Տեղի ունեցավ սխալ որոնման ընթացքում: Խնդրում ենք փորձել կրկին:"
        )

  return render_template("index.html", meaning=meaning, name=name)


if __name__ == "__main__":
  app.run(debug=True)
