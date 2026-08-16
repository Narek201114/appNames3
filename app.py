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
      api_url = "https://hy.wikipedia.org/w/api.php"
      headers = {
          "User-Agent": (
              "AppNameApp/1.0"
              " (https://github.com/; contact@example.com)"
          )
      }

      # Ուղղակիորեն փնտրում ենք «Անուն (անձնանուն)» վերնագրով, ինչպես նաև սովորական տարբերակով
      target_titles = [f"{name} (անձնանուն)", f"{name} (անուն)", name]
      extract = None

      for title in target_titles:
        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "titles": title,
        }

        try:
          response = requests.get(
              api_url, params=params, headers=headers, timeout=8
          )
          data = response.json()
          pages = data.get("query", {}).get("pages", {})
          page_id = list(pages.keys())[0]

          if page_id != "-1":
            text = pages[page_id].get("extract", "")
            # Ստուգում ենք, որ տեքստը պատահաբար քաղաքի մասին չլինի
            if text and "քաղաք" not in text.lower()[:30]:
              extract = text
              source_url = f"https://hy.wikipedia.org/wiki/{title.replace(' ', '_')}"
              break
        except Exception:
          continue

      if extract:
        meaning = extract
      else:
        meaning = (
            f"«{name}» անունն ունի խորը հայկական արմատներ և գեղեցիկ"
            " նշանակություն:"
        )
        source_url = f"https://hy.wikipedia.org/wiki/Special:Search?search={name}"

  return render_template(
      "index.html", meaning=meaning, name=name, source_url=source_url
  )


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=10000)
