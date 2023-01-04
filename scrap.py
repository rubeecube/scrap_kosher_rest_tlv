#

import json

import lxml.html
import lxml.etree as etree
import requests
from io import StringIO
import pandas

url = "https://rabanut.co.il/%D7%97%D7%99%D7%A4%D7%95%D7%A9-%D7%A2%D7%A1%D7%A7%D7%99%D7%9D-%D7%9B%D7%A9%D7%A8%D7%99%D7%9D/page/"
parser = etree.HTMLParser()

rests = []
biz_id = None
for page in range(1, 7):
    html = requests.get(url + str(page)).text
    tree = etree.parse(StringIO(html), parser)
    if biz_id is None:
        biz_id = [biz.attrib['value'] for biz in tree.xpath("//select[@name='business_id']/option") if biz.attrib['value']]
    businesses = tree.xpath("//div[contains(@class, 'kosher_item')]")
    base_url = "https://rabanut.co.il/business/"

    for busines in businesses:
        kosher_date = busines.attrib['data-kosher_date']
        href = busines.find("a").attrib['href']
        res = {
            'kosher_date': kosher_date,
            'href': href,
        }
        for el in busines.findall("a/div/div"):
            res[el.attrib['class']] = el.text.strip()
        rests += [res]

with open('rabanut.json', 'w+') as f:
    json.dump(rests, f, indent=4)

with open('rabanut_ids.json', 'w+') as f:
    json.dump(biz_id, f, indent=4)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
    'Accept': '*/*',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Referer': 'https://www.tzohar.org.il/?page_id=37524',
    'Origin': 'https://www.tzohar.org.il',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-origin',
    # Requests doesn't support trailers
    # 'TE': 'trailers',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}

data = 'action=tzohar_find_rest_by_search&s=\n'

response = requests.post('https://www.tzohar.org.il/wp-admin/admin-ajax.php', headers=headers, data=data)

res = lxml.html.fragment_fromstring(response.text, create_parent='div')
rests = [r for r in res if r.tag == "li"]
tsohar = []
for r in rests:
    tsohar += [
        {
            "city": r.find_class("wpsl-city")[0].text,
            "name": r.find_class("wpsl-name")[0].text,
            "category": ", ".join([x.text for x in r.find_class("category")[0]]),
            "street": r.find_class("wpsl-street")[0].text,
            "full_address": r.find_class("wpsl-street")[0].text + ", " + r.find_class("wpsl-city")[0].text
        }
    ]

with open('tsohar.json', 'w+') as f:
    json.dump(tsohar, f, indent=4)

pandas.read_json("rabanut.json").to_excel("rabanut.xlsx", index=False)
pandas.read_json("tsohar.json").to_excel("tsohar.xlsx", index=False)
pandas.read_json("rabanut.json").to_csv("rabanut.csv", index=False)
pandas.read_json("tsohar.json").to_csv("tsohar.csv", index=False)


