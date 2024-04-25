from xml.dom.minidom import parseString
import scrapy
from bs4 import BeautifulSoup as BS
import json
from datetime import datetime
import math
import re
import sys
import html

class thermofisherPageSpider(scrapy.Spider):
    regionConfig = 'ch' # please check https://www.thermofisher.co.uk/gb/en/change-country.html for 'regionConfig' & langConfig
    langConfig = 'en'  # example : belgium -> thermofisher.be/be/fr/home.html meaning regionConfig = be, langConfig = fr .
                       # example : United Kingdom -> thermofisher.co.uk/gb/en meaning regionConfig = gb, langConfig = en . 
                       # for langConfig, please check the website for availabilities, sometimes it have fr,it,en in one region.
    daPage = ''
    #######################################################

    baseUrl = 'https://www.thermofisher.com/us/en/home/order.html'
    name = 'thermofisherPage'
    pages = []
    # allowed_domains = ['thermofisher.com']
    fileReport = open("report.txt","w")
    start_urls = [baseUrl]
    history = []

    headers_normal = {
        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding':'gzip, deflate, br',
        'accept-language':'en-US,en;q=0.9',
        # 'cache-control':'max-age=0',
        # 'cookie':'locale='+langConfig+'_'+regionConfig.upper()+';',
        # 'Host':'www.thermofisher.ch',
        'sec-ch-ua':'"Chromium";v="97", "Opera GX";v="83", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'sec-fetch-dest':'document',
        'sec-fetch-mode':'navigate',
        'sec-fetch-site':'same-origin',
        'sec-fetch-user':'?1',
        'upgrade-insecure-requests':'1',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.46',
    }
    headers_prod = {
        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding':'gzip, deflate, br',
        'accept-language':'en-US,en;q=0.9',
        # 'cache-control':'max-age=0',
        'cookie':'CK_ISO_CODE=us; CK_LANG_CODE=en;',
        # 'Host':'www.thermofisher.ch',
        'sec-ch-ua':'"Chromium";v="97", "Opera GX";v="83", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'sec-fetch-dest':'document',
        'sec-fetch-mode':'navigate',
        'sec-fetch-site':'same-origin',
        'sec-fetch-user':'?1',
        'upgrade-insecure-requests':'1',
        'user-agent':'PostmanRuntime/7.29.0',
    }
    headers_doc = {
        'accept':'*/*',
        'accept-encoding':'gzip, deflate, br',
        'accept-language':'en-US,en;q=0.9',
        'content-type':'application/json; charset=utf-8',
        # 'cache-control':'max-age=0',
        'cookie':'CK_ISO_CODE=us; CK_LANG_CODE=en;',
        # 'Host':'www.thermofisher.ch',
        'sec-ch-ua':'"Chromium";v="97", "Opera GX";v="83", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'sec-fetch-dest':'empty',
        'sec-fetch-mode':'cors',
        'sec-fetch-site':'same-origin',
        'user-agent':'PostmanRuntime/7.29.0',
    }

    def parse(self, response):
        respUrl = response.url
        respUrl = self.daPage
        # respUrl = 'https://www.thermofisher.com/order/catalog/product/94300320'
        if('/category/' in respUrl):
            yield scrapy.Request(respUrl,callback=self.parseCategory,headers=self.headers_normal,meta={'firstRun':False})
        else:
            yield scrapy.Request(respUrl,callback=self.parseProduct,headers=self.headers_prod)
            
    def parseCategory(self, response):
        respUrl = response.url
        products = response.xpath("//*[@data-element_clicked='family-card-product-title']/@href").getall()
        firstRun = response.meta['firstRun']
        for product in products:
            if('https' not in product):
                product = 'https:'+product
            # product = 'https://www.thermofisher.com/antibody/product/Mouse-IL-17A-AOF-Recombinant-Protein/RP-87768'
            yield scrapy.Request(product,callback=self.parseProduct,headers=self.headers_prod)
            # break #break
        
        # if(firstRun):
        #     try:
        #         maxResults = response.xpath("//*[@class='utility-bar-content listview-width']/text()").get()
        #         reResults = re.findall(r"of (\d+) results",maxResults)[0]
        #         # print(reResults)
        #         count = 2
        #         for x in range(15,int(reResults)+15,15):
        #             #https://www.thermofisher.com/search/browse/category/us/en/90111005/dishes?viewtype=tableview&resultPage=2&resultsPerPage=15
        #             urlCreator = respUrl+"?viewtype=tableview&resultPage="+str(count)+"&resultsPerPage=15"
        #             print(urlCreator)
        #             yield scrapy.Request(urlCreator,callback=self.parseCategory,headers=self.headers_normal,meta={'firstRun':False})
        #             count+=1
        #     except:pass

    def parseProduct(self, response):
        respUrl = response.url
        dataSet = []
        # print(respUrl)
        try:
            rawJson = response.xpath("//*[contains(text(),'PRELOADED_STATE')]/text()").get()
            # print(rawJson)
            if(rawJson is not None):
                regex = re.findall(r"PRELOADED_STATE__ = (.*);",rawJson)[0]
                theJson = json.loads(regex)
                familyId = ''
                try:
                    familyId = theJson['product']['product']['familyId']
                except:
                    familyId = theJson['product']['productId']
                products = theJson['product']['product']['items']
                prices = theJson['prices']['prices']
                breadcrumbs = []
                try:
                    breads = theJson['product']['product']['breadCrumbs']
                    for bread in breads:
                        breadcrumbs.append(bread['name'])
                except:pass
                count = 0
                for product in products:
                    if(len(breadcrumbs)==2):
                        breadcrumbs = ['Home','Shop All Products']
                        try:
                            breads = product['breadcrumbs']
                            for bread in breads:
                                breadcrumbs.append(bread['name'])
                        except:pass
                    productCodes = [] #
                    images = [] #
                    productAttributes = [] #
                    
                    productCodes.append({'codeType':'catalog number','code':product['catalogNumber']})
                    try:
                        imgs = product['images']
                        for img in imgs:
                            images.append(img['path']+"-650.jpg")
                    except:pass
                    
                    attributes = product['specifications']
                    for attribute in attributes:
                        productAttributes.append({'name':attribute['name'],'value':attribute['value']})

                    brand = ''
                    try:
                        brand = product['umbrellaBrand']
                    except:
                        try:
                            brand = product['supplierName']
                        except:pass

                    productDescription = ''
                    try:
                        productDescription+=product['shortDescription']
                    except:pass
                    try:
                        productDescription+=product['productFeatures']
                    except:pass
                    try:
                        productDescription+=product['longDescription']
                    except:pass
                    price = []
                    try:
                        price.append({'quantity':prices[count]['requestedQuantity'], 'price': prices[count]['priceAccess']['status'], 'currency':prices[count]['currency'],'unitSize':product['productSize']})
                    except:
                        try:
                            price.append({'quantity':prices[count]['requestedQuantity'], 'price': prices[count]['priceAccess']['status'], 'currency':prices[count]['currency'],'unitSize':prices[count]['uom']})
                        except:pass
                    data = {
                        'URL':'https://www.thermofisher.com'+product['productUrl'],
                        'productName':product['productTitle'],
                        'productDescription':productDescription,
                        'productCodes':productCodes,
                        'brand':brand,
                        'breadcrumb':'>'.join(breadcrumbs), 
                        'price':price, #array of dict
                        'stock':'',
                        'imageURLs':str(images), 
                        'documents':[],
                        'productAttributes':productAttributes,
                    }
                    dataSet.append(data)
                    count+=1
                # if(familyId not in self.history):
                #     self.history.append(familyId)
                yield scrapy.Request('https://www.thermofisher.com/search/api/documents/family/en/id/'+str(familyId)+'?docTypes=Protocols,Probes%20Handbook,LULL,Vectors,COA,MSDS,Manuals,Brochures,CellLines,Posters,Unitrays,MediaFormulation,TechBulletins,SupportFiles',callback=self.parseDocuments,headers=self.headers_doc,meta={'dataSet':dataSet})
            else:
                dataSet = []
                products = re.findall(r"productDetailViewModel = (.*?);",response.text)[0]
                rawJson = json.loads(products)
                familyId = rawJson['sku'].replace("-",'')
                blankUrl = respUrl.replace(rawJson['sku'],'')

                images = []
                breadcrumbs = []
                try:
                    bread = response.xpath("//*[contains(@class,'hero-breadcrumbs')]//a")
                    for br in bread:
                        breadcrumbs.append(br.xpath("./text()").get().strip())
                except:pass

                productAttributes = []
                try:
                    attributes = response.xpath("//*[contains(@class,'table-spec')]//tr[contains(@class,'product-container-body')]")
                    # print(len(attributes))
                    for attribute in attributes:
                        name = attribute.xpath("./th/h2/text()").get().strip()
                        name = name.replace("\t","").replace("\n","")
                        try:
                            productAttributes.append({'name':name,'value':attribute.xpath("./td/span/text()").get().strip()})
                        except:
                            productAttributes.append({'name':name,'value':attribute.xpath("./td/text()").get().strip()})
                except:pass


                for product in rawJson['packageDetails']:
                    productCodes = [] #
                    try:
                        productCodes.append({'codeType':'catalog number','code':product['sku']})
                    except:pass

                    data = {
                        'URL':blankUrl+product['sku'],
                        'productName':response.xpath("//*[@class='product-name']/text()").get(),
                        'productDescription':response.xpath("//*[@class='product-info-para']/*").getall(),
                        'productCodes':productCodes,
                        'brand':response.xpath("//*[@class='brand-name']/text()").get(),
                        'breadcrumb':'>'.join(breadcrumbs), 
                        'price':'', #array of dict
                        'stock':'',
                        'imageURLs':str(images), 
                        'documents':[],
                        'productAttributes':productAttributes,
                    }
                    dataSet.append(data)
                # if(familyId not in self.history):
                #     # print(familyId)
                #     self.history.append(familyId)
                yield scrapy.Request('https://www.thermofisher.com/search/api/documents/family/en/id/'+str(familyId)+'?docTypes=Protocols,Probes%20Handbook,LULL,Vectors,COA,MSDS,Manuals,Brochures,CellLines,Posters,Unitrays,MediaFormulation,TechBulletins,SupportFiles',callback=self.parseDocuments,headers=self.headers_doc,meta={'dataSet':dataSet})
        except Exception as e:
            self.fileReport.write(respUrl+"-"+str(e)+"\n")
            self.fileReport.flush()
            # print(e)

    def parseDocuments(self,response):
        dataSet = response.meta['dataSet']       
        try:
            documents = []
            rawJson = json.loads(response.text)
            for key,value in rawJson['searchResults'].items():
                # print(key)
                docs = rawJson['searchResults'][key]
                for doc in docs:
                    try:
                        documents.append({'url':doc['path'],'name':doc['title']})
                    except:
                        try:
                            documents.append({'url':doc['downloadUrl'],'name':doc['title']})
                        except:pass

            
            for data in dataSet:
                data['documents'] = documents
                yield(data)
        except Exception as e:
            for data in dataSet:
                yield(data)
            # print(e)