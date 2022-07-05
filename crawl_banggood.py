import requests
import json
from bs4 import BeautifulSoup as bs
import os

api = "https://trans.banggood.com/forwards/load/oscategory/getCategoryData.html"
headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}
langs = {"en-GB","de-DE","fr-FR","pt-PT","it-IT","es-ES","ru-RU","tr-TR","jp-JP","ko-KO","ar-AR"}

cates = {
   "phones": {"cat_id": 1001,"bid": "210703"},
   "electronic":{"cat_id": 2001,"bid": "210704"},
   "industry":{"cat_id": 3001,"bid": "210705"},
   "motorcycles":{"cat_id": 4001,"bid": "210708"},
   "outdoor":{"cat_id": 6001,"bid": "210709"},
   "home":{"cat_id": 12001,"bid": "210710"},
   "furniture":{"cat_id": 12425,"bid": "210710"}
}

params = {
    "cat_id": 1001,
    "page": 1,
    "page_part": 2,
    "direct": 0,
    "rec_uid": "2217658813|1656512922",
    "bid": "210703",
    "sort": 1,
    "sortType": "desc",
    "ori_domain": "www.banggood.com",
    "lang": "en-GB",
    "currency": "USD"
}

def get_product_detail(url):
    resp = requests.get(url,headers=headers)
    soup = bs(resp.text,"lxml")
    detail = soup.find(class_="tab-cnt-detail")
    if detail:
        return detail.text
    return None

def get_detail_by_id(id,lang):
    url = f"https://{lang}.banggood.com/index.php?com=product&t=ajaxGetProductDetails&products_id={id}"
    headers.update({"referer":"https://www.banggood.com"})
    resp = requests.get(url,headers=headers)
    soup = bs(resp.text,"lxml")
    text = soup.text
    return text

def crawl_it(lang):
    params.update({"lang":lang})
    lang = lang.split("-")[0]
    if lang == "en":
        lang = "www"
    params.update({"ori_domain":f"{lang}.banggood.com"})
    for k,v in cates.items():
        params.update(v)
        for i in range(1,10):
            params.update({"page":i})
            for i in range(1,3):
                params.update({"page_part":i})
                resp = requests.get(api,params=params,headers=headers)
                data = resp.json()
                result = data["result"]
                product_list = result["product_list"]
                for product in product_list:
                    product_id = product["products_id"]
                    product_name = product["products_name"]
                    print(product_name)
                    url = product["url"]
                    product_detail = get_detail_by_id(product_id,lang)
                    if not product_detail:
                        product_detail = get_product_detail(url)
                    savedir = f"banggood/{lang}/{k}"
                    if not os.path.exists(savedir):
                        os.makedirs(savedir)
                    with open(f"{savedir}/{product_id}.txt","w",encoding="utf-8") as f:
                        f.write(url+"\n")
                        f.write(product_name+"\n")
                        f.write(product_detail+"\n")


from multiprocessing import Pool

def multi_run():
    p = Pool(4)
    p.map(crawl_it,langs)

def run():
    for lang in langs:
        crawl_it(lang)

if __name__ == "__main__":
    multi_run()
    # run()