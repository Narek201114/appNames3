from bs4 import BeautifulSoup
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
      # Օգտագործում ենք DuckDuckGo-ի ուղղակի HTML որոնումը, որը երբեք չի արգելափակվում
      query = f"{name} անվան նշանակություն"
      search_url = f"https://html.duckduckgo.com/html/?q={query}"

      headers = {
          "User-Agent": (
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
              " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
          )
      }

      try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Գտնում ենք որոնման առաջին արդյունքի հղումը
        first_link = None
        for a in soup.find_all("a", class_="result__url", href=True):
          first_link = a["href"]
          break

        if not first_link:
          # Այլընտրանքային որոնում հղումների համար
          for a in soup.find_all("a", href=True):
            href = a["href"]
            if "uddg=" in href:
              from urllib.parse import parse_qs, urlparse

              parsed_url = urlparse(href)
              captured_url = parse_qs(parsed_url.query).get("uddg")
              if captured_url:
                first_link = captured_url[0]
                break

        # Եթե գտանք հղում, մտնում ենք կարդալու
        if first_link:
          source_url = first_link
          res = requests.get(first_link, headers=headers, timeout=8)
          page_soup = BeautifulSoup(res.text, "html.parser")
          paragraphs = page_soup.find_all("p")

          texts = [
              p.get_text().strip()
              for p in paragraphs
              if len(p.get_text().strip()) > 30
          ]

          if texts:
            meaning = "\n\n".join(texts[:3])
          else:
            meaning = (
                f"«{name}» անվան մասին գտնվել է համապատասխան էջ, սակայն"
                " տեքստը հնարավոր չեղավ ավտոմատ կարդալ:"
            )
        else:
          meaning = f"Ցավոք, «{name}» անվան վերաբերյալ որևէ բան չգտնվեց:"

      except Exception as e:
        meaning = (
            "Որոնման կամ տվյալների բեռնման ընթացքում տեղի ունեցավ սխալ:"
        )

  return render_template(
      "index.html", meaning=meaning, name=name, source_url=source_url
  )


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=10000)
