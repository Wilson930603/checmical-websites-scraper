from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import os
from fake_headers import Headers
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import json
import re
from time import sleep

class FaustAuthPageSelenium():
    regionConfig = 'ch' 
    langConfig = 'en'  
    scrapedItems = 0
    if(langConfig == 'en'):
        baseUrl = 'https://www.faust.ch/shop/tree_an_alpha_lang_uk.htm'
    else:
        baseUrl = 'https://www.faust.ch/shop/tree_an_alpha_lang_de.htm'
    header = Headers(
        browser="chrome",  # Generate only Chrome UA
        os="win",  # Generate only Windows platform
        headers=False # generate misc headers
    )
    customUserAgent = header.generate()['User-Agent']
    def __init__(self,URL='https://www.faust.ch/shop/tree_an_alpha_lang_uk.htm',userName=None,password=None):
        self.driver = self.get_driver()
        self.baseUrl = URL
        self.userName = userName
        self.password = password

    def get_driver(self):
        Options = webdriver.ChromeOptions()
        #Options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        #Options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
        #Options.add_experimental_option('useAutomationExtension', False)
        #Options.add_argument("--disable-blink-features=AutomationControlled")
        Options.add_argument("--headless")
        Options.add_argument("--disable-dev-shm-usage")
        Options.add_argument("--no-sandbox")
        #PROXY = "61.29.96.146:8000"
        #Options.add_argument('--proxy-server=%s' % PROXY)
        Options.add_argument("--disable-extensions")
        Options.add_argument('--start-maximized')
        #Options.add_argument(f"user-agent={customUserAgent}")
        return webdriver.Chrome(ChromeDriverManager().install(),options=Options)

    def login(self):
        self.driver.get(self.baseUrl)
        try:
            self.driver.find_element(By.XPATH,"//input[contains(@name,'USERNAME')]").send_keys(self.userName)
            self.driver.find_element(By.XPATH,"//input[contains(@name,'USERPASS')]").send_keys(self.password)
            self.driver.find_element(By.XPATH,"//input[contains(@class,'LoginBtn')]").click()
            sleep(1)
        except:
            self.driver.close()
            return "Login Failed"
        try:
            failed = self.driver.find_element(By.XPATH,"//p[@class='LoginErrorDesc']")
            self.driver.close()
            return "Login Failed"
        except:pass
    def getProduct(self,driver,Url,first):
        try:
            if first != 0:
                self.driver.get(Url)
                sleep(.5)
            products = driver.find_elements(By.XPATH,"//*[contains(@class,'DbD Col')]/*[@class='DbL']")
            listProducts = []
            for i in products:
                listProducts.append(i.get_attribute("href"))
            if(len(products)>0):
                for count,product in enumerate(listProducts):
                    if('/shop/' in product):
                        urlProduct = product
                    else:
                        urlProduct = 'https://www.faust.ch/shop/'+product
                
                    x = []
                    x.append(self.getProduct(driver,urlProduct,1))
                return x    #yield x
            else:
                temp = driver.find_elements(By.XPATH,"//*[@id='ProdImageTag']")
                images = []
                for i in temp:
                    images.append(i.get_attribute("src"))

                breadCrumbs = []
                tempBread = driver.find_elements(By.XPATH,"//*[@id='WR_BREADCRUMB']//*[@itemprop='name']")
                for i in tempBread:
                    breadCrumbs.append(i.text.strip())
                productDec = ""
                tempProductDec = driver.find_elements(By.XPATH,"//*[@itemprop='description']")
                for i in tempProductDec:
                    productDec += " "+i.text
                data = {
                    'URL':driver.current_url,
                    'groupURL':self.baseUrl,
                    'productName':driver.find_element(By.XPATH,"//*[@class='SEGHEADTEXT']/*[@itemprop='name']").text.strip(),
                    'productDescription':productDec,#html
                    'productCodes':'',
                    'brand':'',#empty
                    'breadcrumb':'>'.join(breadCrumbs), 
                    'price':'', #array of dict
                    'stock':'',
                    'imageURLs':images, 
                    'documents':'',#empty
                    'productAttributes':'',
                }
                try:

                    currency = driver.find_element(By.XPATH,"//th[contains(@class,'DbH ITEMPRICE')]").text
                    currency = currency.split("\n")[1]
                    unit = driver.find_element(By.XPATH,"//th[contains(@class,'DbH Unit')]").text
                    tableHeaders = driver.find_elements(By.XPATH,"//table[@class='DBTable SEGTABLE']//th")
                    theHeaders = []
                    headersClass = []
                    for tableHeader in tableHeaders:
                        tableClass = tableHeader.get_attribute("class") 
                        headersClass.append(tableClass)
                        tableTexts = tableHeader.text
                        try:
                            if('ITEMPRICE' in tableClass):
                                currency = tableTexts[1].text.strip()
                            if('Unit' in tableClass):
                                unit = tableTexts[0].text.strip()
                        except:pass
                        theHeaders.append(''.join(tableTexts).strip().replace('\n',' '))
                    
                    subProducts = driver.find_elements(By.XPATH,"//*[@class='DBTable SEGTABLE']//tr[contains(@class,'DataTableRow')]")

                    for subProduct in subProducts:
                        productCodes = []
                        productAttributes = []
                        price = []
                        stock = ''  # for p['stock']
                        unitSize = ''
                        bulkQty = ''
                        p = data.copy()
                        tds = subProduct.find_elements(By.XPATH,"td")
                        count = 0
                        for td in tds:
                            # tdClass = td.xpath("./@class").get()
                            # print(tdClass)
                            tdClass = headersClass[count]
                            # print(tdClass)
                            tdValue = ''
                            try:
                                tdValue = td.get_attribute("class").strip()
                            except:
                                pass
                            # print(tdValue)
                            if (tdValue != '' or tdValue is not None):
                                try:
                                    if ('Unit' in tdClass):
                                        unitSize = td.text
                                    elif ('Itemno' in tdClass):
                                        productCodes.append({'codeType': theHeaders[count], 'code': td.text})
                                    elif ('StockCol' in tdClass):
                                        stock = td.text
                                    elif ('ITEMPRICE' in tdClass):
                                        price.append({'quantity': 1, 'price': td.text, 'currency': currency,
                                                        'unitSize': str(unitSize) + " " + unit})
                                    elif ('GRADQTY' in tdClass):
                                        bulkQty = td.text
                                    elif ('GRADPRICE' in tdClass):
                                        if (bulkQty.strip() != ''):
                                            price.append({'quantity': str(bulkQty), 'price': td.text, 'currency': currency,
                                                            'unitSize': str(unitSize) + " " + unit})
                                    else:
                                        if (theHeaders[count] != ''):
                                            productAttributes.append({'name': theHeaders[count], 'value': td.text})
                                except Exception as e:
                                    print(e)
                            count += 1
                        p['productAttributes'] = productAttributes
                        p['price'] = price
                        p['stock'] = stock
                        p['productCodes'] = productCodes
                        self.scrapedItems+=1
                        print(p)
                        #yield (p)
                        return p
                except Exception as e:
                    return []
        except Exception as e:
            self.driver.close()
            print({'ERROR':e})
            return {'ERROR':"Failed To Get Item"} 
        
    def main(self):
        try:
            ret = self.login()
            if ret=="Login Failed":
                return {'ERROR': ret}
            c = self.getProduct(self.driver,'',0)
            # for i in self.getProduct(self.driver,'',0):
            #     yield i
            self.driver.close()
            print(c)
            print(f"TOTAL ITEMS SCRPAED: {self.scrapedItems}")
            return c
        except Exception as e:
            self.driver.close()
            return {'ERROR': e}
# t = FaustAuthPageSelenium(userName='aaron.ueckermann@axiomdata.io',password='Ekorra41')
# print(d= t.main())