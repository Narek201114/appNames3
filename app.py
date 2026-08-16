from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Հայտնի անունների բազա, որոնք միշտ անխափան աշխատելու են
NAMES_DATABASE = {
    "նարեկ": (
        "Նարեկ անունը հայկական ծագում ունի, կապված է հայկական վանքերի և Սուրբ"
        " Նարեկ գրքի հետ, նշանակում է աստվածային լույս և հոգևոր ուժ:"
    ),
    "անի": (
        "Անի անունը հին հայկական անուն է, նշանակում է գեղեցիկ, հոգով մաքուր"
        " կամ կապված է մեր պատմական մայրաքաղաք Անիի հետ:"
    ),
    "արմեն": (
        "Արմեն անունը հայկական ծագում ունի, նշանակում է հայ մարդ, հայորդի:"
    ),
    "դավիթ": (
        "Դավիթ անունը եբրայական ծագում ունի, նշանակում է սիրելի, ընտրյալ:"
    ),
    "մերի": (
        "Մերի անունը ծագում է Մարիամ անունից, նշանակում է սիրելի, լուսավոր:"
    ),
    "գայանե": (
        "Գայանե անունը լատինական ծագում ունի, նշանակում է երկրային:"
    ),
}


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
      clean_name = name.lower()

      # 1. Նախ ստուգում ենք մեր բազայում
      if clean_name in NAMES_DATABASE:
        meaning = NAMES_DATABASE[clean_name]
        source_url = "https://hy.wikipedia.org"
      else:
        # 2. Եթե բազայում չկա, փորձում ենք որոնել ինտերնետով
        query = f"{name} անվան նշանակությունը"
        urls_to_try = []

        try:
          with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            for r in results:
              link = r.get("href", "")
              if (
                  link
                  and "wikipedia.org" not in link
                  and "facebook.com" not in link
              ):
                urls_to_try.append(link)
        except Exception:
          pass

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }

        for u in urls_to_try:
          try:
            response = requests.get(u, headers=headers, timeout=5)
            if response.status_code == 200:
              response.encoding = response.apparent_encoding
              soup = BeautifulSoup(response.text, "html.parser")
              paragraphs = soup.find_all("p")
              for p in paragraphs:
                txt = p.get_text().strip()
                if len(txt) > 40 and is_armenian(txt):
                  source_url = u
                  meaning = txt
                  break
              if meaning:
                break
          except Exception:
            continue

        if not meaning:
          meaning = (
              f"Ցավոք, «{name}» անվան վերաբերյալ ստույգ տեղեկություն չգտնվեց:"
          )

  return render_template(
      "index.html", meaning=meaning, name=name, source_url=source_url
  )


if __name__ == "__main__":
  app.run(debug=True)
