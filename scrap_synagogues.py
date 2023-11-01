import json
import lxml.etree as etree
import requests
from io import StringIO
import pandas
import time

def innertext(tag):
    if tag.text is None:
        tag_text = ''
    else:
        tag_text = tag.text.strip()
    if tag.tail is None:
        tag_tail = ''
    else:
        tag_tail = tag.tail.strip()
    return (tag_text + ''.join(innertext(e) for e in tag).strip() + tag_tail).strip()


url = "https://rabanut.co.il/%D7%97%D7%99%D7%A4%D7%95%D7%A9-%D7%91%D7%AA%D7%99-%D7%9B%D7%A0%D7%A1%D7%AA-%D7%91%D7%A2%D7%99%D7%A8/page/"
parser = etree.HTMLParser()

re_cache = False

try:
    with open('syn_urls.json', 'r') as f:
        syns_url = json.load(f)
except:
    re_cache = True

if re_cache:
    syns_url = []
    syn_id = None
    for page in range(1, 5):
        time.sleep(1)
        html = requests.get(url + str(page)).text
        tree = etree.parse(StringIO(html), parser)
        syns_url += [syn.attrib['href'] for syn in tree.xpath("/html/body/div[1]/section/div/div[2]/div[2]/div/div/a")]

    with open('syn_urls.json', 'w+') as f:
        json.dump(syns_url, f, indent=4)

try:
    with open('synagogues.json', 'r') as f:
        syns = json.load(f)
except:
    re_cache = True

if re_cache:
    syns = []

done_urls = [x['url'] for x in syns]
print(f"skipping {len(done_urls)}...")
for i, syn_url in enumerate(syns_url):
    if syn_url in done_urls:
        continue
    html = requests.get(syn_url).text
    tree = etree.parse(StringIO(html), parser)

    fields = [innertext(x) for x in tree.xpath('/html/body/div[1]/section/div/div[2]/div[3]/div/span')]
    values = [innertext(x) for x in tree.xpath('/html/body/div[1]/section/div/div[2]/div[3]/div/div')]
    print(syn_url)
    name_block = tree.xpath("/html/body/div[1]/section/div/div[2]/div[1]/h2")
    try:
        res = {
            'url': syn_url,
            'name': name_block[0].text.strip()
        }
    except:
        print(f"Done {i}/{len(syns_url)}...")
        with open('synagogues.json', 'w+') as f:
            json.dump(syns, f, indent=4)
        pandas.read_json("synagogues.json").to_excel("synagogues_partial.xlsx", index=False)
        pandas.read_json("synagogues.json").to_csv("synagogues_partial.csv", index=False)
        print('go to sleep...')

        time.sleep(60*5)
        html = requests.get(syn_url).text
        tree = etree.parse(StringIO(html), parser)

        fields = [innertext(x) for x in tree.xpath('/html/body/div[1]/section/div/div[2]/div[3]/div/span')]
        values = [innertext(x) for x in tree.xpath('/html/body/div[1]/section/div/div[2]/div[3]/div/div')]
        name_block = tree.xpath("/html/body/div[1]/section/div/div[2]/div[1]/h2")
    for i, f in enumerate(fields):
        res[f] = values[i]
    syns += [res]

with open('synagogues.json', 'w+') as f:
    json.dump(syns, f, indent=4)

pandas.read_json("synagogues.json").to_excel("synagogues.xlsx", index=False)
pandas.read_json("synagogues.json").to_csv("synagogues.csv", index=False)


