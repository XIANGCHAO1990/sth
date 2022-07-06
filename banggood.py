import glob
import os
import json
from multiprocessing import Pool
import threading
import requests
from bs4 import BeautifulSoup as bs
from crawl_banggood import get_detail_by_id,langs,headers

www_path = "banggood/www"

def get_label_id():
    label_dict = {}
    for root,_,files in os.walk(www_path):
        label = root.split("/")[-1]
        id = [f.replace(".txt","") for f in files]
        label_dict[label] = id
    del label_dict["www"]
    return label_dict

def get_url_overview(label,id):
    with open(os.path.join(www_path,label,f"{id}.txt"),"r",encoding="utf-8") as f:
        lines = f.readlines()
    url = lines[0].strip("\n")
    overview = "".join(lines[2:])
    title = lines[1].strip("\n")
    return (url,overview,title)

def get_img_url(url):
    resp = requests.get(url,headers=headers)
    soup = bs(resp.text,"lxml")
    img_ele = soup.find(id="landingImage")
    img_url = img_ele.get("src")
    title = soup.find(class_="product-title-text").text
    return (img_url,title)


def match_detail(lang,label,id):
    url,overview,title = get_url_overview(label,id)
    img_url,_ = get_img_url(url)
    www_content = {
        "product_id":id,
        "img_url":img_url,
        "title":title,
        "url":url,
        "description":overview
    }
    www_json = f"banggood_json/www/{label}"
    if not os.path.exists(www_json):
        os.makedirs(www_json)
    with open(os.path.join(www_json,f"{id}.txt"),"w",encoding="utf-8") as f:
        for _,v in www_content.items():
            f.write(v+"\n")
    
    match_url = url.replace("www.banggood.com",f"{lang}.banggood.com")
    print(match_url)
    match_img_url,match_title = get_img_url(match_url)
    match_overview = get_detail_by_id(id,lang)
    match_content = {
        "product_id":id,
        "img_url":match_img_url,
        "title":match_title,
        "url":match_url,
        "description":match_overview
    }
    match_json = f"banggood_json/{lang}/{label}"
    if not os.path.exists(match_json):
        os.makedirs(match_json)
    with open(os.path.join(match_json,f"{id}.txt"),"a+",encoding="utf-8") as f:
        for _,v in match_content.items():
            f.write(v+"\n")

def run(lang):
    label_dict = get_label_id()
    for label,ids in label_dict.items():
        threads = []
        for id in ids:
            th = threading.Thread(target=match_detail,args=(lang,label,id,))
            threads.append(th)
            # match_detail(lang,label,id)
        for th in threads:
            th.start()
            th.join()


if __name__ == "__main__":
    langs = [lang.split("-")[0] for lang in langs]
    p = Pool(4)
    p.map(run,langs)
    # for lang in langs:
    #     run(lang)