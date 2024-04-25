from xml.dom.minidom import parseString
import scrapy
from bs4 import BeautifulSoup as BS
import json
from datetime import datetime
import math
import re
import sys
import html
from price_parser import Price

class fishersciPriceSpider(scrapy.Spider):
    regionConfig = 'ch' # please check https://www.fishersci.co.uk/gb/en/change-country.html for 'regionConfig' & langConfig
    langConfig = 'en'  # example : belgium -> fishersci.be/be/fr/home.html meaning regionConfig = be, langConfig = fr .
                       # example : United Kingdom -> fishersci.co.uk/gb/en meaning regionConfig = gb, langConfig = en . 
                       # for langConfig, please check the website for availabilities, sometimes it have fr,it,en in one region.
    daPage = ''
    #######################################################
    if(regionConfig == 'gb'):
        baseUrl = 'https://www.fishersci.co.uk/'+regionConfig+'/'+langConfig
        shopUrl = 'https://www.fischersci.co.uk'
    else:
        baseUrl = 'https://www.fishersci.'+regionConfig+'/'+regionConfig+'/'+langConfig
        shopUrl = 'https://www.fishersci.'+regionConfig
    name = 'fishersciPrice'
    pages = []
    
    # allowed_domains = ['fishersci.com']
    start_urls = [baseUrl+"/home.html"]
    history = []

    headers_normal = {
        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding':'gzip, deflate, br',
        'accept-language':'en-US,en;q=0.9',
        'cache-control':'max-age=0',
        'cookie':'locale='+langConfig+'_'+regionConfig.upper()+';',
        'sec-ch-ua':'"Chromium";v="96", "Opera GX";v="82", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'sec-fetch-dest':'document',
        'sec-fetch-mode':'navigate',
        'sec-fetch-site':'same-origin',
        'sec-fetch-user':'?1',
        'upgrade-insecure-requests':'1',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.50',
    }

    headers_json = {
        'accept':'application/json, text/javascript, */*; q=0.01',
        'accept-encoding':'gzip, deflate, br',
        'accept-language':'en-US,en;q=0.9',
        'cookie':'locale='+langConfig+'_'+regionConfig.upper()+';',
        'sec-ch-ua':'"Chromium";v="96", "Opera GX";v="82", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'sec-fetch-dest':'empty',
        'sec-fetch-mode':'cors',
        'sec-fetch-site':'same-origin',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.50',
        'x-requested-with':'XMLHttpRequest'
    }

    def parse(self, response):
        respUrl = response.url
        # respUrl = 'https://www.fishersci.co.uk/gb/en/products/I9C8JVVT/scales.html' #testing
        # respUrl = 'https://www.fishersci.co.uk/shop/products/bd-cytometric-bead-array-rat-tnf-flex-set-standard/15859428' #testing
        respUrl = self.daPage
        yield scrapy.Request(respUrl,callback=self.parseDetails,headers=self.headers_json,meta={'catName':'','groupUrl':'','prodCode':str(1)})

    def parseCategories(self, response):
        respUrl = response.url
        categories = response.xpath("//*[@class='parsys gerericTab1']//*[@class='general_item_list']//li/a")
        for category in categories:
            try:
                catName = category.xpath("./text()").get()
                catUrl = category.xpath("./@href").get()
                # print(catName)
                identifier = re.findall(r"products/(.*?)/",catUrl)[0]
                # identifier = 'I9C8JXAD' #testing
                urlCreator = self.baseUrl + '/catalog/service/browse/products?storeId=10652&offset=0&Ns=default&identifier='+identifier
                yield scrapy.Request(urlCreator,callback=self.parseProducts,headers=self.headers_json,meta={'firstRun':True,'catName':catName})
                # break #testing
            except:
                print(category)
    
    def parseProducts(self, response):
        respUrl = response.url
        catName = response.meta['catName']
        firstRun = response.meta['firstRun']
        rawJson = json.loads(response.text)
        products = rawJson['productResults']
        for product in products:
            try:
                recordCount = product['recordCount']
                if(recordCount==1):
                    groupUrl = ''
                elif(recordCount>1):
                    groupUrl = self.shopUrl+product['productUrl']
                
                prodUrlRaw = re.findall(r"/shop/products/(.*?)/",product['productUrl'])[0]
                prodCreator = self.shopUrl+'/shop/products/'+prodUrlRaw
                subProducts = product['itemCatalogNo']
                for subProduct in subProducts:
                    urlProduct = prodCreator + '/' + str(subProduct)
                    #urlProduct = 'https://www.fishersci.ch/shop/products/pyrex-labware-class-b-borosilicate-glass-burette-ptfe-key/12164222' #testing
                    yield scrapy.Request(urlProduct,callback=self.parseDetails,headers=self.headers_json,meta={'catName':catName,'groupUrl':groupUrl,'prodCode':str(subProduct)})
            except:
                pass
            # break #testing

        if(firstRun):
            maxRange = rawJson['aggrRecordListSize']
            for x in range(0,maxRange,30):
                urlNext = respUrl.replace('offset=0','offset='+str(x))
                yield scrapy.Request(urlNext,callback=self.parseProducts,headers=self.headers_json,meta={'firstRun':False,'catName':catName})

    def parseDetails(self, response):
        respUrl = response.url
        print(respUrl)
        catName = response.meta['catName']
        groupUrl = response.meta['groupUrl']
        prodCode = response.meta['prodCode']

        productCodes = []
        productCodes.append({'codeType':'product code','code':prodCode})
        try:
            code = response.xpath("//*[@name='partNum']/@value").get()
            if(code is not None):
                productCodes.append({'codeType':'manufacturer code','code':code})
        except:pass

        productDescription = ''
        try:
            productDescription+=''.join(response.xpath("//*[@class='subhead']/p[1]").getall()).strip()
            productDescription = productDescription.strip()
        except Exception as e:pass
        try:
            productDescription+=''.join(response.xpath("//*[@id='descriptionIsVisible']/following-sibling::*").getall()).strip()
            productDescription = productDescription.strip()
        except Exception as e:pass
        productDescription = productDescription.replace("\n","")

        price = []
        try:
            tempPrice = response.xpath("//*[@itemprop='unitText']/span/text()").get().strip().split(' / ')
            tempDat1 = str(response.xpath("//*[@itemprop='price']/@content").get())
            data1 = tempPrice[0].replace(tempDat1,'').strip()
            data2 = tempPrice[1]

            price.append({'quantity':'1', 'price': tempDat1, 'currency':data1,'unitSize':data2})
        except Exception as e:pass

        if(price==[]):
            try:
                tablePrices = response.xpath("//*[@class='specs_table_full']//tr")
                for tablePrice in tablePrices:
                    try:
                        priceQty = tablePrice.xpath("./td[1]/text()").get().strip()
                        priceNum = ''.join(tablePrice.xpath("./td[2]//text()").getall()).strip().split(' / ')
                        data1 = Price.fromstring(priceNum[0]) #32.44 CHF
                        # print(data1)
                        data2 = priceNum[1] #unit

                        price.append({'quantity':priceQty, 'price': data1.amount_text, 'currency':data1.currency,'unitSize':data2})
                    except:pass
            except Exception as e:print(e)


        breadcrumbs = ''
        try:
            tempBreads = response.xpath("//*[@class='breadcrumb']//*[@itemprop='position']/following-sibling::text()").getall()
            count=0
            for tempBread in tempBreads:
                if(count==0):
                    breadcrumbs+=tempBread.strip()
                    count+=1
                else:
                    breadcrumbs+=">"+tempBread.strip()
                
        except:pass

        stock = ''
        try:
            stock = response.xpath("//*[@id='SKUQtyContainer']/span/text()").get()
        except:pass
        if(stock == ''):
            try:
                stock = response.xpath("//*[@id='SKUQtyContainer']/following-sibling::span/text()").get()
            except:pass
        images = []
        try:
            imageList = response.xpath("//*[@id='productImage']/@src").getall()
            for img in imageList:
                images.append(img)
        except:pass

        brand = ''
        try:
            rawJson = json.loads(response.xpath("//*[@type='application/ld+json']/text()").get().replace("//sku page","").replace("//family page",""),strict=False)
            brand = html.unescape(rawJson['brand']['name'])
        except Exception as e:pass

        productAttributes = []
        try:
            addAtts = response.xpath("//*[contains(.,'Additional Details :')]/following-sibling::span")
            for addAtt in addAtts:
                attName = addAtt.xpath("./strong/text()").get()
                attVal = addAtt.xpath("./strong/following-sibling::text()").get().strip()
                if(attVal is not None):
                    productAttributes.append({'name':attName,'value':attVal})
        except:pass

        try:
            tables = response.xpath("//*[@class='specs_data']//tr")
            for table in tables:
                try:
                    attName = ''.join(table.xpath("./td[1]//text()").getall()).strip()
                    attVal = ''.join(table.xpath("./td[2]//text()").getall()).strip()
                    productAttributes.append({'name':attName,'value':attVal})
                except:pass
        except Exception as e:print(e)

        data = {
            'URL':respUrl,
            'groupURL':groupUrl,
            'productName':response.xpath("//h1[@itemprop='name']/text()").get().strip(),
            'productDescription':productDescription,#html
            'productCodes':productCodes,#array of dict
            'brand':brand,
            'breadcrumb':breadcrumbs, 
            'price':price, #array of dict
            'stock':stock,
            'imageURLs':images, 
            'documents':'',
            'productAttributes':productAttributes, 
        }

        yield({'price':data['price']})
        # yield scrapy.Request('https://www.fishersci.ch/shop/products/documents/'+str(prodCode),callback=self.parseDocuments,headers=self.headers_normal,meta={'data':data})

    def parseDocuments(self, response):
        respStatus = response.status
        data = response.meta['data']

        docs = []
        if(respStatus==404):
            yield(data)
        else:
            documents = response.xpath("//*[contains(@id,'qa_document_link')]")
            for document in documents:
                documentLink = document.xpath("./@href").get()
                documentName = document.xpath(".//img/following-sibling::text()").get().strip()
                docs.append({'name':documentName,'value':documentLink})
            data['documents'] = docs

            yield(data)

                

        # print(data)

