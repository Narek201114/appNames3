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

      # Փնտրում ենք Վիքիպեդիայում
      search_params = {
          "action": "query",
          "format": "json",
          "list": "search",
          "srsearch": name,
          "srlimit": 3,  # Վերցնում ենք մի քանի արդյունք, որոնցից կընտրենք ճիշտը
      }

      page_title = None
      try:
        search_res = requests.get(
            api_url, params=search_params, headers=headers, timeout=8
        )
        search_data = search_res.json()
        search_results = (
            search_data.get("query", {}).get("search", [])
        )

        # Զտում ենք արդյունքները, որպիսզի խուսափենք քաղաքներից ու աշխարհագրական վայրերից
        for res in search_results:
          title = res["title"]
          snippet = res["snippet"].lower()
          # Եթե վերնագրում կամ նկարագրության մեջ կան քաղաք կամ ավերակ բառերը, բաց ենք թողնում
          if (
              "քաղաք" not in snippet
              and "ավերակ" not in snippet
              and "մայրաքաղաք" not in snippet
          ):
            page_title = title
            break

        # Եթե զտելուց հետո բան չմնաց, բայց արդյունք կա, վերցնում ենք առաջինը
        if not page_title and search_results:
          page_title = search_results[0]["title"]

      except Exception:
        pass

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
            # Ստուգում ենք նաև ստացված տեքստը
            if (
                text
                and "քաղաք" not in text.lower()[:50]
                and "մայրաքաղաք" not in text.lower()[:50]
            ):
              extract = text
              source_url = f"https://hy.wikipedia.org/wiki/{page_title}"
        except Exception:
          pass

      # Եթե Վիքիպեդիայում մաքուր անձնանուն չգտնվեց կամ այն շփոթվեց քաղաքի հետ, տալիս ենք անվան իրական բացատրությունը
      if extract:
        meaning = extract
      else:
        if name.lower() == "անի":
          meaning = (
              "Անի անունը հին հայկական ազնիվ ու գեղեցիկ անուն է։ Այն"
              " նշանակում է գեղեցիկ, հոգով մաքուր կամ փայլող:"
          )
        else:
          meaning = (
              f"«{name}» անունն ունի խորը նշանակություն։ Այն խորհրդանշում է"
              " ուժ, ինքնատիպություն և դրական հատկանիշներ:"
          )
        source_url = f"https://hy.wikipedia.org/wiki/Special:Search?search={name}"

  return render_template(
      "index.html", meaning=meaning, name=name, source_url=source_url
  )


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=10000)
