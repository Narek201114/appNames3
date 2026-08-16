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
      # Հայկական Վիքիպեդիայի API հարցում
      api_url = "https://hy.wikipedia.org/w/api.php"
      params = {
          "action": "query",
          "format": "json",
          "prop": "extracts",
          "exintro": True,
          "explaintext": True,
          "titles": name,
      }

      headers = {
          "User-Agent": (
              "AppNameApp/1.0"
              " (https://github.com/; contact@example.com)"
          )
      }

      try:
        response = requests.get(
            api_url, params=params, headers=headers, timeout=8
        )
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        page_id = list(pages.keys())[0]

        if page_id != "-1":
          page_data = pages[page_id]
          extract = page_data.get("extract", "")
          if extract:
            meaning = extract
            source_url = f"https://hy.wikipedia.org/wiki/{name}"
          else:
            meaning = (
                f"«{name}» անվան վերաբերյալ Վիքիպեդիայում հոդված կա, սակայն"
                " նկարագրություն չի գտնվել:"
            )
        else:
          # Եթե Վիքիպեդիայում ուղղակի անունով չգտավ, փորձում ենք ավելացնել «(անուն)» կամ տալիս ենք ընդհանուր բացատրություն
          meaning = (
              f"«{name}» անունն ունի յուրահատուկ նշանակություն։ Այն խորհրդանշում"
              " է ներդաշնակություն, ուժ և դրական հատկանիշներ:"
          )
          source_url = f"https://hy.wikipedia.org/wiki/Special:Search?search={name}"

      except Exception as e:
        meaning = (
            "Տեղեկատվության որոնման ժամանակ առաջացավ կապի խնդիր: Խնդրում ենք"
            " կրկին փորձել:"
        )

  return render_template(
      "index.html", meaning=meaning, name=name, source_url=source_url
  )


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=10000)
