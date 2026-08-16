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
            # 1. Google որոնում
            query = f"{name} անվան նշանակություն"
            search_url = f"https://www.google.com/search?q={query}"
            
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 2. Գտնում ենք առաջին հղումը
            first_link = None
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("/url?q="):
                    first_link = href.split("/url?q=")[1].split("&")[0]
                    break
            
            # 3. Մտնում ենք այդ հղումով և վերցնում պարբերությունները
            if first_link:
                try:
                    res = requests.get(first_link, headers=headers, timeout=5)
                    page_soup = BeautifulSoup(res.text, "html.parser")
                    paragraphs = page_soup.find_all("p")
                    
                    # Վերցնում ենք առաջին մի քանի պարբերությունը
                    texts = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30]
                    meaning = "\n\n".join(texts[:3]) # Առաջին 3 պարբերությունը
                except:
                    meaning = "Ցավոք, հնարավոր չեղավ տվյալներ կարդալ կայքից:"
            else:
                meaning = "Ոչինչ չգտնվեց:"

    return render_template("index.html", meaning=meaning, name=name)

if __name__ == "__main__":
    app.run(debug=True)
