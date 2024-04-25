from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import re
from time import sleep
import random
from datetime import datetime
class ThermofisherAuthPageSelenium():
    signInUrl = 'https://www.thermofisher.com/account-center/signin-identifier.html'
    getLinkUrl = 'https://www.thermofisher.com/search/browse/category/us/en/90140059/pipette-tips'
    #'https://www.thermofisher.com/order/catalog/product/TLR102R-Q?SID=srch-srp-TLR102R-Q'
    #'https://www.thermofisher.com/order/catalog/product/991SP12?SID=srch-srp-991SP12'

    def __init__(self,url='https://www.thermofisher.com/search/browse/category/us/en/90140059/pipette-tips',userName=None,password=None):
        self.userName= userName
        self.password = password
        self.ProductLinks = []
        self.proxyList = []
        self.usedProxy = []
        self.maxProxy = 1000
        with open("proxy.txt") as file:
            for line in file: 
                line = line.strip() #or some other preprocessing
                self.proxyList.append(line) #storing everything in memory!
        self.logFile = datetime.now().strftime("THERMOFISHER_PAGE_Selenium_%Y_%m_%d-%I-%M-%S_%p")
        with open(f'{self.logFile}.log','w') as f:
            f.write('THERMOFISHER PAGE SELENIUM LOGS\n')
        self.driver = self.get_driver()
        self.getLinkUrl = url

    def get_driver(self):
        for i in range(self.maxProxy):
            Options = webdriver.ChromeOptions()
            #Options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
            Options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
            Options.add_experimental_option('useAutomationExtension', False)
            Options.add_argument("--disable-blink-features=AutomationControlled")
            Options.add_argument("--headless")
            Options.add_argument("--disable-dev-shm-usage")
            Options.add_argument("--no-sandbox")
            while(True):
                tempProxy = self.proxyList[random.randint(0,len(self.proxyList)-1)]
                if tempProxy not in self.usedProxy:
                    self.usedProxy.append(tempProxy)
                    break
                else:
                    continue
            PROXY = tempProxy
            Options.add_argument('--proxy-server=%s' % PROXY)
            Options.add_argument('--ignore-certificate-errors')
            Options.add_argument("--disable-extensions")
            Options.add_argument('--start-maximized')
            Options.add_argument("window-size=1920x1080")
            Options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36 OPR/65.0.3467.48")
            try:
                driver = webdriver.Chrome(ChromeDriverManager().install(),options=Options)
                driver.get(self.signInUrl)
                sleep(7)
                driver.find_element_by_xpath("//input[contains(@id,'username-field')]")
                return driver
            except Exception as e:
                print(e)
                print(f'Proxy Failed: {tempProxy}, Using next proxy!')
                self.writeLogs(str(e))
                self.writeLogs(f'{i+1}) Proxy Failed: {tempProxy}, Using next proxy!\n')
                driver.close()
    def logIn(self):
        self.driver.get(self.signInUrl)
        sleep(7)
        try:
            a = self.driver.find_element(By.XPATH,"//h1[contains(@id,'main-error')]")
            print(a.text)
            return "Thermofiser System Down"
        except:pass
        name = self.driver.find_element(By.XPATH,"//input[contains(@id,'username-field')]")
        name.send_keys(self.userName)
        self.driver.find_element(By.XPATH,"//input[contains(@id,'next-button')]").click()
        sleep(5)

        self.driver.find_element(by=By.XPATH,value="//input[contains(@id,'password-field')]").send_keys(self.password)
        self.driver.find_element(by=By.XPATH,value="//input[contains(@id,'signin-button')]").click()
        sleep(15)
    def getPageLinks(self):
        self.driver.get(self.getLinkUrl)
        sleep(1)
        products = self.driver.find_elements(By.XPATH,"//*[@data-element_clicked='family-card-product-title']")
        for i in products:
            self.ProductLinks.append(i.get_attribute("href"))
        self.writeLogs(f'TOTAL PRODUCT LINKS: {len(self.ProductLinks)}')
    def getPrice(self,links):
        for link in links:
            self.driver.get(link)
            sleep(1.5)
            self.writeLogs(f'Scraping: {link}\n')

            dataSet = []
            rawJson = self.driver.find_element(By.XPATH,"//*[contains(text(),'PRELOADED_STATE')]")
            regex = re.findall(r"PRELOADED_STATE__ = (.*);",rawJson.get_attribute("innerHTML"))[0]
            theJson = json.loads(regex)
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
            dataset = []
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
                    try:
                        productAttributes.append({'name':attribute['name'],'value':attribute['value']})
                    except:pass
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
                #dataset.append(data)
                count+=1
                
                dataSet.append(data)

                #yield data

            if familyId!='':
                try:
                    newCheck = 'https://www.thermofisher.com/search/api/documents/family/en/id/'+str(familyId)+'?docTypes=Protocols,Probes%20Handbook,LULL,Vectors,COA,MSDS,Manuals,Brochures,CellLines,Posters,Unitrays,MediaFormulation,TechBulletins,SupportFiles'
                    self.driver.get(newCheck)
                    sleep(0.5)
                    documents = []
                    doc = self.driver.find_element(By.XPATH,"//pre").text
                    rawJson = json.loads(doc)
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
                        #self.SCRAPEDITEMS+=1
                        data['documents'] = documents
                        yield(data)
                except Exception as e:
                    print(e)
                    for data in dataSet:
                        #self.SCRAPEDITEMS+=1
                        yield(data)
    def writeLogs(self, data,dump=False):
        with open(f'{self.logFile}.log','a') as f:
            if dump:
                json.dump(data, f)
                f.write('\n')
            else:
                f.write(data)            
    def main(self):
        try:
            if self.maxProxy == len(self.usedProxy):
                print(f"{self.maxProxy} PROXIES Used, none found working. Terminating.")
                self.writeLogs(f"{self.maxProxy} PROXIES Used, none found working. Terminating.\n")
                return
            data = self.logIn()
            if data == "Thermofiser System Down":
                yield {'Login Failed':data}
                self.driver.close()
                return
            self.getPageLinks()
            for i in self.getPrice(self.ProductLinks):
                print(i)
                self.writeLogs(i,True)
                yield i
            self.driver.close()
            
        except Exception as e:
            self.driver.close()

# c = ThermofisherAuthPageSelenium(userName='aaron.ueckermann@googlemail.com',password='AxiomPassword123!')
# for i in c.main():
#     print(i)
