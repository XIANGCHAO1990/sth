import requests
from bs4 import BeautifulSoup as bs
import os
import glob
from multiprocessing import Pool

en_path = "zaful/en"
headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    'Connection': 'close'
    }
requests.adapters.DEFAULT_RETRIES = 5

def get_product_detail(url):
    resp = requests.get(url,headers=headers)
    soup = bs(resp.text,"lxml")
    descrip = soup.find(class_="xxkkk").text
    title = soup.find("h1").text
    img_url = soup.find(id="js-goodsGalleryShow").find("img").get("src")
    return (descrip,title,img_url)

def crawl_labels(href,label):
    label_path = os.path.join(en_path,label)
    if not os.path.exists(label_path):
        os.makedirs(label_path)
    for i in range(1,4):
        url = f"{href}g_{i}.html"
        resp = requests.get(url,headers=headers)
        soup = bs(resp.text,'lxml')
        products = soup.find(id="js_proList")
        products = soup.find_all(class_="img-hover-wrap")
        for pro in products:
            a = pro.find("a")
            product_url = a.get("href")
            sku = product_url.split("=")[-1]
            descrip,title,img_url = get_product_detail(product_url)
            with open(os.path.join(label_path,f"{sku}.txt"),"w",encoding="utf-8") as f:
                f.write(sku+"\n")
                f.write(title+"\n")
                f.write(label+"\n")
                f.write(img_url+"\n")
                f.write(product_url+"\n")
                f.write(descrip)


def get_labels(ele):
    title = ele.get("title").lower().replace(" ","")
    href = ele.get("href")
    if title not in ["new","sale","swimwear"]:
        crawl_labels(href,title)

def run():
    if not os.path.exists(en_path):
        os.makedirs(en_path)
    url = "https://www.zaful.com/"
    resp = requests.get(url,headers=headers)
    soup = bs(resp.text,"lxml")
    title_eles = soup.find_all(class_="nav-title")
    for ele in title_eles:
        get_labels(ele)

langs = {"de","fr","pt","it","es","ru","tr","jp","ko","ar"}
def multi_run(label_path):
    label = label_path.split("/")[-1]
    for pro_path in glob.glob(label_path+"/*")[:700]:
        sku = pro_path.split("/")[-1]
        with open(pro_path,"r",encoding="utf-8") as f:
            lines = f.readlines()
        url = lines[4]
        print(url)
        for lang in langs:
            if not os.path.exists(f"zaful/{lang}/{label}"):
                os.makedirs(f"zaful/{lang}/{label}")
            url = url.replace("www",lang)
            descrip,title,img_url = get_product_detail(url)
            with open(f"zaful/{lang}/{label}/{sku}.txt","w",encoding="utf-8") as f:
                f.write(sku+"\n")
                f.write(title+"\n")
                f.write(label+"\n")
                f.write(img_url+"\n")
                f.write(url+"\n")
                f.write(descrip)

if __name__ == "__main__":
    # multi_run()
    paths = [label_path for label_path in glob.glob("zaful/en/*")]
    p = Pool(4)
    p.map(multi_run,paths)
    # for path in paths:
    #     multi_run(path)