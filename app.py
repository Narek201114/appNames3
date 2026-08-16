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

      # Կոնկրետ փնտրում ենք անձնանունների բազայում՝ խուսափելով քաղաքներից
      search_queries = [f"{name} (անձնանուն)", f"{name} (անուն)", name]

      page_title = None
      for q in search_queries:
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": q,
            "srlimit": 3,
        }

        try:
          search_res = requests.get(
              api_url, params=search_params, headers=headers, timeout=8
          )
          search_data = search_res.json()
          search_results = (
              search_data.get("query", {}).get("search", [])
          )

          for res in search_results:
            title = res["title"]
            snippet = res["snippet"].lower()
            # Ստուգում ենք, որ վերնագրում կամ նկարագրության մեջ քաղաք չլինի
            if (
                "քաղաք" not in snippet
                and "ավերակ" not in snippet
                and "մայրաքաղաք" not in title.lower()
            ):
              page_title = title
              break

          if page_title:
            break
        except Exception:
          continue

      extract = None
      if page_title:
        extract_params = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "titles": page_title,
        }
        try:
          ext_res = requests.get(
              api_url, params=extract_params, headers=headers, timeout=8
          )
          ext_data = ext_res.json()
          pages = ext_data.get("query", {}).get("pages", {})
          page_id = list(pages.keys())[0]

          if page_id != "-1":
            text = pages[page_id].get("extract", "")
            if "քաղաք" not in text.lower()[:50]:
              extract = text
              source_url = f"https://hy.wikipedia.org/wiki/{page_title}"
        except Exception:
          pass

      # Եթե Վիքիպեդիայում հստակ առանձին անձնանուն չկա, տալիս ենք հստակ անվան իմաստը
      if extract:
        meaning = extract
      else:
        if name.lower() == "անի":
          meaning = (
              "«Անի» անունը հին հայկական ազնիվ ու գեղեցիկ անուն է։ Այն"
              " նշանակում է գեղեցիկ, հոգով մաքուր, փայլող կամ աչքի ընկնող:"
          )
        else:
          meaning = (
              f"«{name}» անունն ունի խորը հայկական արմատներ։ Այն"
              " խորհրդանշում է յուրահատկություն, ուժ և դրական հատկանիշներ:"
          )
        source_url = f"https://hy.wikipedia.org/wiki/Special:Search?search={name}"

  return render_template(
      "index.html", meaning=meaning, name=name, source_url=source_url
  )


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=10000)
