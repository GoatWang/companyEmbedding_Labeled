import aiohttp
import asyncio
import async_timeout
import os
from os import listdir
import time
from bs4 import BeautifulSoup
from selenium import webdriver
import queue
import threading
import pandas as pd
import string
from preprocessing import preprocessing
import json

## Build Queue
input_companies = queue.Queue()
fail_log = queue.Queue()

## Fill Queue with companyDict
files = listdir("labelData")
files = [file for file in files if "csv" in file]
for file in files:
    df_comps = pd.read_csv("labelData/" + file, index_col=None, header=None)

    companyTupleList = []
    def buildTupleList(row):
        companyTuple = (row[0], row[1])
        companyTupleList.append(companyTuple)

    df_comps.apply(buildTupleList, axis=1)

    for company, related in companyTupleList:
        companyDict = {}
        companyDict['name'] = company
        companyDict['query'] = "{} product".format(company)
        companyDict['related'] = related

        exclude = set(string.punctuation)
        companyName = ''.join(p for p in company if p not in exclude)
        companyName = companyName.replace(" ", "_").lower()  ##Build self.companyName
        companyDict['filename'] = companyName

        companyDict['targetCompany'] = file.replace(".csv", "")
        input_companies.put(companyDict)

class newBingCrawler:
    def __init__(self, loop):
        self.loop = loop  ##self.loop

    def __call__(self):
        async def fetch_coroutine(client, url):
            with async_timeout.timeout(10):
                try: 
                    async with client.get(url) as response:
                        assert response.status == 200
                        contentType = str(response.content_type)
                        if 'html' in str(contentType).lower():
                            html = await response.text()
                            soup = BeautifulSoup(html ,'lxml')
                            [x.extract() for x in soup.findAll('script')]
                            [x.extract() for x in soup.findAll('style')]
                            [x.extract() for x in soup.findAll('nav')]
                            [x.extract() for x in soup.findAll('footer')]
                            self.companyInfo += soup.text
                        return await response.release()
                except:
                    self.failLinks.append(url)

        async def main(loop):
            #driver = webdriver.Chrome()
            #driver = webdriver.PhantomJS()
            driver = webdriver.PhantomJS(executable_path="D:\\phantomjs.exe")
            url = "https://www.bing.com/"
            driver.get(url)
            elem = driver.find_element_by_xpath('//*[@id="sb_form_q"]')
            elem.send_keys(self.query)
            elem = driver.find_element_by_xpath('//*[@id="sb_form_go"]')
            elem.submit()
            html = driver.page_source
            driver.close()

            soup = BeautifulSoup(html, 'lxml')
            Links = soup.find_all('a')

            Goodlinks = []
            for link in Links:
                linkstr = str(link)
                if (('http' in linkstr) and ('href' in linkstr) and (not 'href="#"' in linkstr) and (not 'href="http://go.microsoft' in linkstr)and (not 'microsofttranslator' in linkstr)):
                    Goodlinks.append(link)

            urls = [link['href'] for link in Goodlinks]
            #print(self.query, "Good links have been found!")

            headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
            async with aiohttp.ClientSession(loop=loop, headers=headers, conn_timeout=5 ) as client:
                tasks = [fetch_coroutine(client, url) for url in urls]
                await asyncio.gather(*tasks)
 
        while True:
            try:
                self.companyAnnotation = input_companies.get(timeout=1)   ##Build self.query
            except:
                break
            
            ## build self attr
            self.companyInfo = ""  ##Build self.companyInfo
            self.failLinks = []  ##Build self.failLinks
            self.comapanyName = self.companyAnnotation['name']
            self.query = self.companyAnnotation['query']  ##Build self.query
            self.filename = self.companyAnnotation['filename']  ##Build self.filename
            self.targetCompany = self.companyAnnotation['targetCompany']  ##Build self.targetCompany
            self.related = self.companyAnnotation['related']  ##Build self.related

            ## start running loop
            self.loop.run_until_complete(main(self.loop))

            ## After loop
            fail_log.put({self.filename:self.failLinks})
            
            ## Stroe unprocessed file into comapnyEmbedding 
            targetDirectory1 = "comapnyEmbedding/" + self.targetCompany
            if not os.path.isdir(targetDirectory1):
                os.mkdir(targetDirectory1)

            if self.related == 1:
                relatedTargetDirectory1 = targetDirectory1 + "/related"
                if not os.path.isdir(relatedTargetDirectory1):
                    os.mkdir(relatedTargetDirectory1)
                file = open(relatedTargetDirectory1 + "/" + self.filename, 'w', encoding='utf8')
            else:
                file = open(targetDirectory1 + "/" + self.filename, 'w', encoding='utf8')
            
            file.write(self.companyInfo)
            file.close()

            ## Stroe processed file into processedCompanyEmbedding 
            targetDirectory2 = "processedCompanyEmbedding/" + self.targetCompany
            if not os.path.isdir(targetDirectory2):
                os.mkdir(targetDirectory2)

            if self.related == 1:
                relatedTargetDirectory2 = targetDirectory2 + "/related"
                if not os.path.isdir(relatedTargetDirectory2):
                    os.mkdir(relatedTargetDirectory2)
                file = open(relatedTargetDirectory2 + "/" + self.filename, 'w', encoding='utf8')
            else:
                file = open(targetDirectory2 + "/" + self.filename, 'w', encoding='utf8')

            file.write(preprocessing(self.companyInfo))
            file.close()

            print(id(self), self.comapanyName + " success")

threads = []
for i in range(7):
    loop = asyncio.new_event_loop()
    #loop = asyncio.get_event_loop()
    newthread = threading.Thread(target=newBingCrawler(loop))
    newthread.start()
    threads.append(newthread)

for thread in threads:
    thread.join()

logs = []
while True:
    try:
        logLi = fail_log.get(timeout=1)
        if logLi != []:
            logs.append(logLi)
    except:
        break

with open("log.txt", 'w', encoding='utf8') as fp:
    json.dump(logs, fp)

