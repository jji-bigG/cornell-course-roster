import os
import requests
from bs4 import BeautifulSoup
import json

url = "https://cals.cornell.edu/education/degrees-programs"
os.makedirs("htmls", exist_ok=True)

if not os.path.exists("htmls/cals_studies_list.html"):

    response = requests.get(url)

    with open("htmls/cals_studies_list.html", "w") as f:
        f.write(response.text)

    response_text = response.text
else:
    with open("htmls/cals_studies_list.html") as f:
        response_text = f.read()

soup = BeautifulSoup(response_text, "lxml")


def save_row(row: dict, filename):
    with open(filename, "a") as f:
        f.write(json.dumps(row) + "\n")


def extract_cards(cards, section):
    print(f"extracting cards for {section}")
    for card in cards:
        if not card:
            print("no card found")
            continue
        card_data = {}
        a = card.find("a", class_="link")
        card_data["title"] = a.get_text()
        card_data["url"] = a["href"]

        front = card.find("div", class_="degree-card-front")
        if not front:
            print("no front")
            continue

        card_data["description"] = front.find("p").get_text()
        field = card.find(
            "p",
            class_="study field field--type-entity-reference field--label-hidden field__items",
        )
        if field:
            card_data["field"] = field.get_text()
        else:
            print("no field")
            card_data["field"] = None

        back = card.find(
            "div",
            class_="clearfix text-formatted field field--type-text-long field--label-hidden field__item",
        )
        if back:
            back = back.get_text()
        else:
            # print("no back")
            back = None
        card_data["back"] = back
        card_data["section"] = section

        save_row(card_data, "cals-studies-list.jsonl")


# Find all panels
panels = soup.select("div.field--name-field-program-items .panel.panel-default")
# print(f"found {len(panels)} panels")

for panel in panels:
    sections = [
        s.find("h3", class_="heading").get_text()
        for s in panel.find_all("div", class_="section-intro-copy text-center")
    ]
    p = panel.find("button", class_="data-gtm-openProgram").get_text().strip()
    print(f"looking at panel {p}")
    if p == "Degree Programs":
        p = "programs"
    elif p == "Careers":
        p = "career"

    if p == "Non-Degree Programs":
        cards = panel.find_all(
            "div",
            class_="degree-card paragraph paragraph--type--program-card paragraph--view-mode--default",
        )
        # print(f"found {len(cards)} cards under that {p}")
        extract_cards(cards, p)

    for s in sections:
        trans_s = (
            s.lower()
            .strip()
            .translate(str.maketrans({" ": "-", "/": "-", "&": "amp", "+": ""}))
        )
        id = f"{trans_s}-{p.lower().strip()}"
        section = panel.find(
            "div",
            class_=f"collapse",
            id=id,
        )
        if not section:
            print(f"no section found for {s} where id is {id}")
            continue
        cards = section.find_all(
            "div",
            class_="degree-card paragraph paragraph--type--program-card paragraph--view-mode--default",
        )
        print(f"found {len(cards)} cards under that section {s}")

        extract_cards(cards, s)
