# coding:utf-8

import requests
import urllib.parse
import os
import re
from bs4 import BeautifulSoup
from time import sleep

class YahooScraper:

    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0'
    headers = {'User-Agent': ua}

    def __init__(self, query=""):
        self.yahoo = 'https://search.yahoo.co.jp/image/search?oq=&ei=UTF-8&p='
        self.query = urllib.parse.quote(query)
        self.folderpath = desktop_path = os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH") + "\\Desktop"
        pass

    def setQuery(self, query):
        self.query = urllib.parse.quote(query)
        url = self.yahoo + query
        return url

    def makeQueryFolder(self):
        #self.folderpath = path
        path = self.folderpath + "\\" + urllib.parse.unquote(self.query)
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as err:
           print("OS error: {0}".format(err))
           sys.exit("could not make folder")
        self.output = path
        print(self.output)


    def getSoup(self, URL):
        soup = BeautifulSoup(requests.get(URL, headers=self.headers).content,'lxml')
        return soup

    def guessNextURL(self, preurl):
        pattern = r".*&b=([0-9]+)"
        mached = re.match(pattern, preurl)
        try:
            prenumber = mached.group(1)
            url = preurl + re.sub(pattern, "&b=" + str(int(prenumber) + 20), preurl)
        except:
            url = preurl +"&xargs=2"+ "&b=21"
        return url

    def nextURL(self, soup):
        sp1 = soup.find(id="Sp1")
        sp1 = sp1.find_all(text="次へ")
        link = sp1[0].find_parent("a")
        return link["href"]
        pass

    def getImageURLs(self, soup):
        images =[]
        pattern = r"^(http.?(.*?))\|"
        grid = soup.find(id="gridlist").prettify()
        grid = BeautifulSoup(grid, 'lxml')
        urls = grid.find_all("img")

        for imgtag in urls:
            result = urllib.parse.unquote(imgtag)
            matched = re.match(pattern, imgtag["rel"])
            images.append(matched.group(1))
        return images

    def nextPage(self):
        pass
    def emptyChecker(self, soup):
        a = soup.find(string="に一致する画像はみつかりませんでした。")
        return isinstance(a ,type(None))

    def saveImage(self, url):
        res = requests.get(url, headers=self.headers)
        pattern = r"([^\?]*)"#avoid xxx.jpg?width=520
        filename = res.url.split('/')[-1]
        filename = re.match(pattern, filename)
        filename = filename.group(1)
        try:
            with open(self.output + "\\" + filename, 'wb') as f: # imgフォルダに格納
                f.write(res.content)
        except:
            print("Could not download: " + res.url)
            pass

if __name__ == '__main__':
    s = YahooScraper()
    url = s.setQuery("吉野家")
    s.makeQueryFolder()
    while True:
        soup = s.getSoup(url)
        if s.emptyChecker(soup) is not True:break
        imglist = s.getImageURLs(soup)
        for url in imglist:
            s.saveImage(url)
            sleep(1)

        url = s.nextURL(soup)
        print(url)
        sleep(1)
    print("finish downloading")
