import scrapy
from bs4 import BeautifulSoup as BS
import json
from datetime import datetime
import math
import re
import sys

class vwrPageSpider(scrapy.Spider):
    locale = 'ch' #please check www.vwr.com for locale, example : Switzerland -> ch.vwr.com -> locale = 'ch'
    #######################################################
    baseUrl = 'https://'+locale+'.vwr.com'
    
    name = 'vwrPage'
    pages = []
    # start_urls = ["https://us.vwr.com/store/category/adhesives/3617154"]
    history = []
    # def __init__(self, url):
    #     self.start_urls = url

    def parse(self, response):
        self.baseUrl = 'https://'+self.locale+'.vwr.com'

        check = response.xpath("//*[@id='searchKeywordId']/@value").get()
        # print(check)
        if(check is None):
            yield scrapy.Request(response.url,callback=self.parseProduct,meta={'catName':''})
        else:
            yield scrapy.Request(response.url+"&sortOrder=2",callback=self.parseCategory,meta={'catName':'','firstRun':False,'page':1,'url':response.url},dont_filter=True)
        # return {'url':response.text}
        # categories = response.xpath("//*[@class='a-z_categorylist']//a")
        # for category in categories:
        #     catName = category.xpath("./text()").get()
        #     catUrl = category.xpath("./@href").get()
        #     urlCreator = self.baseUrl+catUrl+"?sortOrder=2"
        #     yield scrapy.Request(urlCreator,callback=self.parseCategory,meta={'catName':catName,'firstRun':True,'page':1,'url':self.baseUrl+catUrl+"?sortOrder=2"},dont_filter=True)
        #     # break #testing

    def parseCategory(self, response):
        baseUrl = response.url
        catName = ''
        firstRun = response.meta['firstRun']
        url = response.meta['url']
        page = response.meta['page']
        retry = 1
        try:
            retry = response.meta['retry']
        except:pass
        if('noSearchResults' in baseUrl):
            urlNext = url
            if(retry<30):
                yield scrapy.Request(urlNext,callback=self.parseCategory,meta={'catName':catName,'firstRun':False,'page':page,'url':url,'retry':retry+1},dont_filter=True)
            
        products = response.xpath("//*[contains(@id,'productLink')]//a/@href").getall()

        for product in products:
            urlCreator = self.baseUrl+product
            yield scrapy.Request(urlCreator,callback=self.parseProduct,meta={'catName':catName})
        
        # if(firstRun and products!=[]):
        #     pagination=response.xpath("//*[contains(@class,'pagination-label')]/text()").get()
        #     totalPage = re.findall(r" of ([^>]*)",pagination)[0]
        #     countPage = math.floor(int(totalPage.replace(",",""))/16)

        #     if(countPage>1):
        #         for x in range(2,countPage+1):
        #             urlNext = url+"&pageNo="+str(x)
        #             yield scrapy.Request(urlNext, callback=self.parseCategory, meta={'catName':catName,'firstRun':False,'page':x,'url':url})


    def parseProduct(self,response):
        baseUrl = response.url
        # print(response.text)
        catName = response.meta['catName']
        
        try:
            productId = re.findall(r"/product/(.*?)/",baseUrl)[0]
        except:productId = ''
        productCodes = []
        if(productId!=''):
            productCodes.append({'codeType':'Product Id','code':productId})
        try:
            breadcrumb = response.xpath("//*[contains(@class,'breadcrumb-item')]//*[@itemprop='name']/text()").getall()
            breadcrumb.append(response.xpath("//*[@class='breadcrumb-item active']/text()").get().strip())
            breadcrumb = str(breadcrumb)
        except:breadcrumb = []
        try:
            images = response.xpath("//img[contains(@src,'/bigweb/')]/@src").getall()
        except:images = []
        
        productList = []
        productAttributes = response.xpath("//*[@class='textBodyText expander']/div[not(contains(@class,'textBodyText')) and not(contains(@class,'textBulletPoint')) and not(contains(@class,'textBodyText')) and contains(@class,'text')]")
        try:
            for prodAtt in productAttributes:
                prodKey = prodAtt.xpath("./b/text()").get().strip()
                prodVal = prodAtt.xpath("./b/following-sibling::text()").get().strip()
                productList.append({'name':prodKey,'value':[prodVal]})
        except:pass


        data = {
            # 'mainCat':catName,
            'URL':baseUrl,
            'productName':response.xpath("//h1/*[@itemprop='name']/text()").get(),
            'productdescription':''.join(response.xpath("//*[@class='product_desc_container']/div[contains(@class,'textBodyText ')]").getall()),#html
            'productCodes':productCodes,#array of dict
            'brand':response.xpath("//*[@itemprop='manufacturer']//text()").get(),
            'breadcrumb':breadcrumb, 
            'price':[], #array of dict
            'productAttributes':productList, 
            'imageURLs':str(images), 
        }
        # print(productId)
        
        if(productId!=''):
            urlCreator = self.baseUrl+"/store/services/catalog/json/stiboSpecificationsRender.jsp?productId="+str(productId)+"&catalogNumber="
            yield scrapy.Request(urlCreator,callback=self.parseSpecifications,meta={'data':data,'productId':productId},dont_filter=True)

    def parseSpecifications(self, response):
        # print(response.url)
        data = response.meta['data']
        productId = response.meta['productId']
        lines = response.xpath("//tr")
        tempAttributes = data['productAttributes'].copy()
        try:
            x = []
            for line in lines:
                vals = []
                tds = line.xpath("./td")
                count = 1
                for td in tds:
                    if(count==1):
                        name = td.xpath("./text()").get()
                        count+=1
                    else:
                        vals.append(td.xpath("./text()").get())
                temp = {'name':name,'value':vals}
                x.append(temp)

            data['productAttributes'] = tempAttributes + x #list
        except:pass
        
        urlCreator = self.baseUrl+"/store/services/catalog/json/stiboOrderTableRender.jsp?productId="+str(productId)+"&catalogNumber=&discontinuedflag=&specialCertRender=false&staticPage="
        yield scrapy.Request(urlCreator,callback=self.parseOrderTable,meta={'data':data,'productId':productId},dont_filter=True)

    def parseOrderTable(self, response):
        print(response.url)
        data = response.meta['data']
        product = response.meta['productId']

        priceSearch = []

        ignoreSups = ['VWR Catalog Number','Unit','Price','Quantity','Supplier No.']
        
        xCompile = []
        subs = response.xpath("//div[contains(@id,'ifpParam')]")
        tempSups = {}
        for sub in subs:
            x = data.copy()
            
            sups = sub.xpath("./following-sibling::tr[@class='product-row-main'][1]")
            if(len(sups)==0):
                sups = sub.xpath("./following-sibling::tbody[1]/tr[@class='product-row-main'][1]")
            tempAttributes = data['productAttributes'].copy()
            tempProductCodes = data['productCodes'].copy()
            tempPrice = data['price'].copy()
            vwrNew = False
            for sup in sups:
                unitData = ''
                tds = sup.xpath("./td")
                for td in tds:
                    tdKey = td.xpath("./@data-title").get()
                    # print(tdKey)
                    tdValue = ''.join(td.xpath(".//text()").getall()).strip()
                    if(tdKey not in ignoreSups):
                        tempAttributes.append({'name':tdKey,'value':tdValue})

                    if(tdKey == 'Supplier No.'):
                        tempProductCodes.append({'codeType':'Supplier No.','code':tdValue})
                    if(tdKey == "VWR Catalog Number"):
                        tempProductCodes.append({'codeType':"Catalog Code",'code':td.xpath(".//*[@itemprop='sku']/text()").get()})
                        vwrNew = True
                    if(tdKey == "Unit"):
                        unitData = td.xpath("./span/text()").get().strip()
                    if(tdKey == "Price"):
                        tdsku = td.xpath("./@id").get().replace("LA","")
                        tempPrice.append({'quantity':'1','unitSize':unitData,'sku':tdsku,'currency':'','price':''})
                        priceSearch.append(tdsku)
            
            if(vwrNew):
                x['productAttributes'] = tempAttributes
                x['productCodes'] = tempProductCodes
                x['price'] = tempPrice
            
                xCompile.append(x)
            else:
                xCompile[-1]['price'] = xCompile[-1]['price'] + tempPrice
                            
        if(priceSearch!=[]):
            urlCreator = self.baseUrl+"/store/services/pricing/json/skuPricing.jsp?skuIds="+str(','.join(priceSearch))
            yield scrapy.Request(urlCreator,callback=self.parsePrices,meta={'x':xCompile})

    def parsePrices(self,response):
        x = response.meta['x']
        prices = json.loads(response.text)
        compiledResult = []
        for p in x:
            for y in range(0,len(p['price'])):
                srcPrc,srcCrc = self.searchPrice(prices,p['price'][y]['sku'])
                p['price'][y]['price'] = srcPrc
                p['price'][y]['currency'] = srcCrc
            yield(p)
        #     compiledResult.append(p)
        # return(compiledResult)

    def searchPrice(self,prices,sku):
        for price in prices:
            if(price['skuId']==sku):
                salePrice = price['salePrice'].isdigit()
                listPrice = price['listPrice'].isdigit()
                if(salePrice<listPrice):
                    return price['salePrice'],price['currencyCode']
                else:
                    return price['listPrice'],price['currencyCode']
