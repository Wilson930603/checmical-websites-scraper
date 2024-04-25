from xml.dom.minidom import parseString
import scrapy
from bs4 import BeautifulSoup as BS
import json
from datetime import datetime
import math
import re
import sys
import html
import requests
from collections import Counter
from latest_user_agents import get_latest_user_agents,get_random_user_agent

class faustBulkSpider(scrapy.Spider):
    filename = 'faustBulk'
    locale = 'ch' # please check https://www.faust.co.uk/gb/en/change-country.html for 'locale' & lang
    lang = 'en'  # example : belgium -> faust.be/be/fr/home.html meaning locale = be, lang = fr .
                       # example : United Kingdom -> faust.co.uk/gb/en meaning locale = gb, lang = en . 
                       # for lang, please check the website for availabilities, sometimes it have fr,it,en in one region.
    #######################################################
    if(lang == 'en'):
        baseUrl = 'https://www.faust.ch/shop/tree_an_alpha_lang_uk.htm'
    else:
        baseUrl = 'https://www.faust.ch/shop/tree_an_alpha_lang_de.htm'
        
    name = 'faustBulk'
    pages = []
    start_urls = [baseUrl]
    history = []

    linkListHistory = 0
    linkList = []

    custom_settings={
        'DOWNLOADER_MIDDLEWARES' : {
        #'flasks.middlewares.flasksDownloaderMiddleware': 543,
            'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
             'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
        #        #                                                     ^^^
            #  'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
                #'scrapy_crawlera.CrawleraMiddleware': 610,
        },
        'CONCURRENT_REQUESTS':250,
        'CONCURRENT_REQUESTS_PER_IP':1,
        'DOWNLOAD_TIMEOUT':15,
        'ITEM_PIPELINES':{
            'flasks.pipelines.CSVPipeline': 300,
        },
        'USER_AGENT':''
    }
    
    headers_normal = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-encoding':'gzip, deflate, br',
        'Accept-language':'en-US,en;q=0.9',
        # 'cache-control':'max-age=0',
        # 'cookie':'locale='+lang+'_'+locale.upper()+';',
        # 'Host':'www.faust.ch',
        # 'sec-ch-ua':'"Chromium";v="97", "Opera GX";v="83", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'Sec-Fetch-Dest':'document',
        'Sec-Fetch-Mode':'navigate',
        'Sec-Fetch-Site':'same-origin',
        'Sec-Fetch-User':'?1',
        'Upgrade-Insecure-Requests':'1',
        # 'User-Agent':'PostmanRuntime/7.29.0',
        'User-Agent':get_random_user_agent()
    }


    def parse(self, response):
        UID = ''
        try:
            UID = response.meta['UID']
        except:pass
        firstTime = True
        firstTimeUID = True
        try:
            firstTime = response.meta['firstTime']
        except:pass
        try:
            firstTimeUID = response.meta['firstTimeUID']
        except:pass

        if(firstTime):
            yield scrapy.Request(self.baseUrl, callback = self.parse, headers=self.headers_normal,priority=50,meta={'UID':'','firstTime':False,'proxy':None})
        else:
            products = response.xpath("//*[contains(@class,'DbD Col')]/*[@class='DbL']/@href").getall()
            for product in products:
                if('/shop/' in product):
                    urlProduct = 'https://www.faust.ch'+product
                else:
                    urlProduct = 'https://www.faust.ch/shop/'+product
                try:
                    urlProduct = re.findall(r"([^>]*)\?UID",urlProduct)[0]
                    urlProduct = urlProduct.replace("?UID","")
                except Exception as e:pass
                self.linkList.append(urlProduct)

            linkListNow = len(list(set(self.linkList)))
            print(linkListNow)
            if(linkListNow>self.linkListHistory):
                self.linkListHistory = linkListNow
                print('next')
                nextCode = response.xpath("//*[@id='WR_TEXTBUTTON_FORWARD']//*[@name='MOVE']/@value").get()
                if(firstTimeUID):
                    UID = 'UID='+response.xpath("//*[@id='WR_TEXTBUTTON_FORWARD']//*[@name='UID']/@value").get()
                    print("FIRST")
                if(len(self.linkList)>1100):
                    firstTimeUID = False
                    try:
                        UID = 'UID='+response.xpath("//*[@id='WR_TEXTBUTTON_FORWARD']//*[@name='UID']/@value").get()
                    except:
                        UID = None
                if(UID is not None):
                    urlNext = self.baseUrl+"?"+UID+"&MOVE="+str(nextCode)
                    yield scrapy.Request(urlNext, callback = self.parse, headers=self.headers_normal,priority=50,meta={'UID':UID,'firstTime':False,'firstTimeUID':firstTimeUID,'proxy':None})
                else:
                    print(len(self.linkList))
                    print(len(list(set(self.linkList))))
                    for urlProduct in self.linkList:
                        yield scrapy.Request(urlProduct, callback = self.parseProducts, headers=self.headers_normal,priority=1)
    
    def parseProducts(self, response):
        print(response.url)
        try:
            groupUrl = response.meta['group']
        except:
            groupUrl = ''
        products = response.xpath("//*[contains(@class,'DbD Col')]/*[@class='DbL']/@href").getall()
        if(len(products)>0):
            for product in products:
                if('/shop/' in product):
                    urlProduct = 'https://www.faust.ch'+product
                else:
                    urlProduct = 'https://www.faust.ch/shop/'+product
                try:
                    urlProduct = re.findall(r"([^>]*)\?UID",urlProduct)[0]
                    urlProduct = urlProduct.replace("?UID","")
                except Exception as e:pass
                yield scrapy.Request(urlProduct, callback = self.parseProducts, headers=self.headers_normal, meta={'group':response.url},priority=3)
                # break
        else:
            #do normal parse
            respUrl = response.url
            images = []
            try:
                temp = response.xpath("//*[@id='ProdImageTag']/@src").getall()
                for te in temp:
                    images.append(te)
            except:pass
            
            data = {
                'URL':respUrl,
                'groupURL':groupUrl,
                'productName':response.xpath("//*[@class='SEGHEADTEXT']/*[@itemprop='name']/text()").get().strip(),
                'productDescription':response.xpath("//*[@itemprop='description']").getall(),#html
                'productCodes':'',
                'brand':'',#empty
                'breadcrumb':'>'.join(response.xpath("//*[@id='WR_BREADCRUMB']//*[@itemprop='name']/text()").getall()).strip(), 
                'price':'', #array of dict
                'stock':'',
                'imageURLs':images, 
                'documents':'',#empty
                'productAttributes':'',
            }
            
            currency = ''
            unit = ''
            tableHeaders = response.xpath("//*[@class='DBTable SEGTABLE']//th")
            theHeaders = []
            for tableHeader in tableHeaders:
                tableClass = tableHeader.xpath("./@class").get()
                tableTexts = tableHeader.xpath(".//text()").getall()
                try:
                    if('ITEMPRICE' in tableClass):
                        currency = tableTexts[1].strip()
                    if('Unit' in tableClass):
                        unit = tableTexts[0].strip()
                except:pass
                theHeaders.append(' '.join(tableTexts).strip())
                
            subProducts = response.xpath("//*[@class='DBTable SEGTABLE']//tr[contains(@class,'DataTableRow')]")
            # print(len(subProducts))
            
            for subProduct in subProducts:
                productCodes = []
                productAttributes = []
                price = []
                stock = '' #for p['stock']
                unitSize = ''
                bulkQty = ''
                p = data.copy()
                tds = subProduct.xpath("./td")
                # print(tds)
                count = 0
                for td in tds:
                    # print(td)
                    tdClass = td.xpath("./@class").get()
                    tdValue=''
                    try:
                        tdValue = td.xpath("./text()").get().strip()
                    except:pass
                    if(tdValue!=''):
                        if('Unit' in tdClass):
                            unitSize = tdValue
                        elif('Itemno' in tdClass):
                            productCodes.append({'codeType':theHeaders[count],'code':tdValue})
                        elif('StockCol' in tdClass):
                            stock = td.xpath("./@title").get()
                        elif('ITEMPRICE' in tdClass):
                            price.append({'quantity':1, 'price': tdValue, 'currency':currency,'unitSize':str(unitSize)+" "+unit})
                        elif('GRADQTY' in tdClass):
                            bulkQty = tdValue
                        elif('GRADPRICE' in tdClass):
                            if(bulkQty.strip()!=''):
                                price.append({'quantity':str(bulkQty), 'price': tdValue, 'currency':currency,'unitSize':str(unitSize)+" "+unit})
                        else:
                            if(theHeaders[count]!=''):
                                productAttributes.append({'name':theHeaders[count],'value':tdValue})
                    count+=1
                p['productAttributes']=productAttributes
                p['price'] = price
                p['stock'] = stock
                p['productCodes'] = productCodes
                yield(p)

            
        
