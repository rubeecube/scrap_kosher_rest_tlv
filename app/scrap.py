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

with open('Storage/rabanut.json', 'w+') as f:
    json.dump(rests, f, indent=4)

with open('Storage/rabanut_ids.json', 'w+') as f:
    json.dump(biz_id, f, indent=4)

pandas.read_json("Storage/rabanut.json").to_excel("Storage/rabanut.xlsx", index=False)
pandas.read_json("Storage/rabanut.json").to_csv("Storage/rabanut.csv", index=False)


