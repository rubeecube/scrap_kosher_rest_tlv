import json
import lxml.etree as etree
import requests
from io import StringIO
import pandas
import time
import os


def innertext(tag, strip_text=True):
    if tag.text is None:
        tag_text = ''
    else:
        if strip_text:
            tag_text = tag.text.strip()
        else:
            tag_text = tag.text
    if tag.tail is None:
        tag_tail = ''
    else:
        if strip_text:
            tag_tail = tag.tail.strip()
        else:
            tag_tail = tag.tail
    if strip_text:
        return (tag_text + ''.join(innertext(e, strip_text) for e in tag).strip() + tag_tail).strip()
    else:
        return (tag_text + ''.join(innertext(e, strip_text) for e in tag) + tag_tail)


url = "https://rabanut.co.il/%D7%97%D7%99%D7%A4%D7%95%D7%A9-%D7%9E%D7%A7%D7%95%D7%95%D7%90%D7%95%D7%AA/page/"
parser = etree.HTMLParser()

re_cache = False

try:
    with open('Storage/mikve_urls.json', 'r') as f:
        mikves_url = json.load(f)
except:
    re_cache = True

if re_cache:
    mikves_url = []
    mikve_id = None
    for page in range(1, 5):
        time.sleep(1)
        html = requests.get(url + str(page)).text
        tree = etree.parse(StringIO(html), parser)
        mikves_url += [mikve.attrib['href'] for mikve in tree.xpath("/html/body/div[1]/section/div/div[2]/div[2]/div/div/a")]

    with open('Storage/mikve_urls.json', 'w+') as f:
        json.dump(mikves_url, f, indent=4)

try:
    with open('Storage/mikvaot.json', 'r') as f:
        mikves = json.load(f)
except:
    re_cache = True

if re_cache:
    mikves = []

done_urls = [x['url'] for x in mikves]
print(f"skipping {len(done_urls)}...")
for i, mikve_url in enumerate(mikves_url):
    if mikve_url in done_urls:
        continue
    html = requests.get(mikve_url).text
    tree = etree.parse(StringIO(html), parser)

    fields = [innertext(x) for x in tree.xpath('/html/body/div[1]/section/div/div[2]/div[3]/div/span')]
    values = [innertext(x, False) for x in tree.xpath('/html/body/div[1]/section/div/div[2]/div[3]/div/div')]
    labels = ", ".join([innertext(x) for x in tree.xpath('/html/body/div[1]/section/div/div[2]/div[4]/div/span')])
    print(mikve_url)
    name_block = tree.xpath("/html/body/div[1]/section/div/div[2]/div[1]/h2")
    try:
        res = {
            'url': mikve_url,
            'name': name_block[0].text.strip(),
            'labels': labels
        }
    except:
        print(f"Done {i}/{len(mikves_url)}...")
        with open('Storage/mikvaot.json', 'w+') as f:
            json.dump(mikves, f, indent=4)
        pandas.read_json("Storage/mikvaot.json").to_excel("Storage/mikvaot_partial.xlsx", index=False)
        pandas.read_json("Storage/mikvaot.json").to_csv("Storage/mikvaot_partial.csv", index=False)
        print('go to sleep...')

        time.sleep(60*5)
        html = requests.get(mikve_url).text
        tree = etree.parse(StringIO(html), parser)

        fields = [innertext(x) for x in tree.xpath('/html/body/div[1]/section/div/div[2]/div[3]/div/span')]
        values = [innertext(x, False) for x in tree.xpath('/html/body/div[1]/section/div/div[2]/div[3]/div/div')]
        labels = ", ".join([innertext(x) for x in tree.xpath('/html/body/div[1]/section/div/div[2]/div[4]/div/span')])
        name_block = tree.xpath("/html/body/div[1]/section/div/div[2]/div[1]/h2")
        res = {
            'url': mikve_url,
            'name': name_block[0].text.strip(),
            'labels': labels
        }
    for i, f in enumerate(fields):
        try:
            res[f] = values[i]
        except:
            pass
    mikves += [res]

with open('Storage/mikvaot.json', 'w+') as f:
    json.dump(mikves, f, indent=4)

pandas.read_json("Storage/mikvaot.json").to_excel("Storage/mikvaot.xlsx", index=False)
pandas.read_json("Storage/mikvaot.json").to_csv("Storage/mikvaot.csv", index=False)
os.rename("Storage/mikvaot.json", "Storage/mikvaot_bak.json")


