from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import os
from fake_headers import Headers
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.common.exceptions import TimeoutException
import json
import re
import math
from time import sleep
class VwrAuthBulkSelenium():
    getLinkUrl = 'https://us.vwr.com/store/catalog/vwr_products.jsp'

    locale = 'us'
    baseUrl = 'https://'+locale+'.vwr.com'
    
    header = Headers(
        browser="chrome",  # Generate only Chrome UA
        os="win",  # Generate only Windows platform
        headers=False # generate misc headers
    )
    customUserAgent = header.generate()['User-Agent']
    def __init__(self,fileName=None,userName=None,password=None):
        self.userName= userName
        self.password = password
        self.categoryLinks = []
        self.productLinks = []
        self.driver = self.get_driver()
        self.fileName = fileName
        if '.json' not in self.fileName:
            self.fileName =f'outputs/{fileName}.json'
        with open(self.fileName, "w") as f:
            f.write('[\n')
        #GET PRICES
    def parsePrices(self,xCompile):
        x = xCompile
        loadData = self.driver.find_element(By.XPATH,"//body")
        prices = json.loads(loadData.text)
        compiledResult = []
        for p in x:
            for y in range(0,len(p['price'])):
                srcPrc,srcCrc = self.searchPrice(prices,p['price'][y]['sku'])
                p['price'][y]['price'] = srcPrc
                p['price'][y]['currency'] = srcCrc

            with open(self.fileName, "a") as f:
                json.dump(p, f)
                f.write(',\n')

    def searchPrice(self,prices,sku):
        for price in prices:
            if(price['skuId']==sku):
                salePrice = price['salePrice'].isdigit()
                listPrice = price['listPrice'].isdigit()
                if(salePrice<listPrice):
                    return price['salePrice'],price['currencyCode']
                else:
                    return price['listPrice'],price['currencyCode']

        
    def get_driver(self):
        Options = webdriver.ChromeOptions()
        #Options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        Options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
        Options.add_experimental_option('useAutomationExtension', False)
        Options.add_argument("--disable-blink-features=AutomationControlled")
        Options.add_argument("--headless")
        Options.add_argument("--disable-dev-shm-usage")
        Options.add_argument("--no-sandbox")
        #PROXY = "61.29.96.146:8000"
        #Options.add_argument('--proxy-server=%s' % PROXY)
        Options.add_argument("--disable-extensions")
        Options.add_argument('--start-maximized')
        Options.add_argument("window-size=1920x1080")
        Options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36 OPR/65.0.3467.48")
        return webdriver.Chrome(ChromeDriverManager().install(),options=Options)
    
    def getCategoryLinks(self):
        try:
            self.categoryLinks = [cat.get_attribute("href") for cat in self.driver.find_elements(By.XPATH,"//*[@class='a-z_categorylist']//a")]
        except:
            return
    def getProductLinks(self,link):
        self.driver.get(link)
        try:
            sleep(1)
            pgNum = self.driver.find_element(By.XPATH,"//div[contains(@class,'col-xs-12 col-sm-3 pagination-label')]").text
            pgNum = math.ceil(int(pgNum.split(" ")[-1].replace(",",""))/32)
            for i in range(pgNum):

                self.driver.get(f"{link}?pageSize=32&pageNo={i+1}")       
                data = self.driver.page_source
                if 'Why do I have to complete a CAPTCHA?' in data:
                    self.driver.back()
                    break
                print(f'LINK: {self.driver.current_url}')
                sleep(1)
                products = self.driver.find_elements(By.XPATH,"//*[contains(@id,'productLink')]//a")
                self.productLinks = self.productLinks + [product.get_attribute('href') for product in products]
                # for product in products:
        except Exception as e:
            print(e)
            pass    #     self.productLinks.append(product.get_attribute("href"))
        
    def logIn(self):
        self.driver.get(self.getLinkUrl)
        #self.driver.implicitly_wait(5)
        sleep(3)
        try:
            coockie = self.driver.find_element_by_id('impliedsubmit')

            coockie.click()
            sleep(3)
        except:pass

        try:
            wait(self.driver, 8).until(EC.element_to_be_clickable((By.XPATH,"//input[contains(@id,'fb_submit')]"))).click()
        #driver.find_element(By.XPATH,"//input[contains(@value,'Log in')]").click()
            sleep(3)
            username = wait(self.driver,1).until(EC.presence_of_element_located((By.XPATH,"//input[contains(@id,'email')]")))
            username.send_keys(self.userName)
            passw = wait(self.driver,1).until(EC.presence_of_element_located((By.XPATH,"//input[contains(@id,'password')]")))         
            passw.send_keys(self.password)
            wait(self.driver,1).until(EC.presence_of_element_located((By.XPATH,"//button[contains(@id,'btn-login')]")))
            wait(self.driver, 1).until(EC.element_to_be_clickable((By.XPATH,"//button[contains(@id,'btn-login')]"))).click()                     
            sleep(6)
        except TimeoutException as e:
            print(e)
            self.driver.close()
        except Exception as ex:
            print(ex)
            self.driver.close() 
    
    def getProduct(self,link):
        #MAIN PRODUCT PAEG
        print(f'LINK: {link}')

        try:
            productId = re.findall(r"/product/(.*?)/",link)[0]
        except:productId = ''
        productCodes = []
        if(productId!=''):
            productCodes.append({'codeType':'Product Id','code':productId})
        try:
            tempBread = self.driver.find_elements(By.XPATH,"//*[contains(@class,'breadcrumb-item')]//span")
            breadcrumb = []
            for i in tempBread:
                breadcrumb.append(i.text)
            breadcrumb.append(self.driver.find_element(By.XPATH,"//li[contains(@class,'breadcrumb-item active')]").text.strip())
            breadcrumb = str(breadcrumb)
        except:breadcrumb = []
        try:
            img = self.driver.find_elements(By.XPATH,"//img[contains(@src,'/bigweb/')]")
            images =[]
            for i in img:
                images.append(i.get_attribute("src"))
        except:images = []

        productList=[]

        try:
            self.driver.find_element(By.XPATH,"//a[contains(@class,'boldTextBig')]").click()
        except Exception as e:
            pass
        try:
            cert = self.driver.find_elements(By.XPATH,"//div[contains(@class,'textCertifications')]")
            pack = self.driver.find_element(By.XPATH,"//div[contains(@class,'textPackaging')]")
            if len(cert)>1:
                prodCert = cert[1].text.split(':')
            else:
                prodCert = cert[0].text.split(':') 
            prodCert[0]+=":"
            productList.append({'name':prodCert[0],'value':[prodCert[1]]})
            prodPack = pack.text.split(":")
            productList.append({'name':prodPack[0]+":",'value':[prodPack[1]]})
        except:pass
        productDesc =""
        try:
            productDesc = self.driver.find_element(By.XPATH,"//*[@class='product_desc_container']/div[contains(@class,'textBodyText ')]").text.split("Certifications:")[0]
        except:
            pass
        data = {
            # 'mainCat':catName,
            'URL':self.driver.current_url,
            'productName':self.driver.find_element(By.XPATH,"//h1/*[@itemprop='name']").text,
            'productdescription': productDesc,#html
            'productCodes':productCodes,#array of dict
            'brand':self.driver.find_element(By.XPATH,"//*[@itemprop='manufacturer']").text,
            'breadcrumb':breadcrumb, 
            'price':[], #array of dict
            'productAttributes':productList, 
            'imageURLs':str(images), 
        }
        urlCreator = self.baseUrl+"/store/services/catalog/json/stiboSpecificationsRender.jsp?productId="+str(productId)+"&catalogNumber="
        self.driver.get(urlCreator)
        sleep(.5)

            #SPECIFICATION
        try:
            tempData =[]
            tempAttributes = data['productAttributes'].copy()

            t = self.driver.find_elements(By.XPATH,"//tr")
            for tr in t:
                tempTr = tr.find_elements(By.TAG_NAME,"td")
                
                tempData.append({'name':tempTr[0].text,'value':tempTr[1].text})
                
            data['productAttributes'] = tempAttributes + tempData #list
        except:
            pass

        urlCreator = f"{self.baseUrl}/store/services/catalog/json/stiboOrderTableRender.jsp?productId={productId}&catalogNumber=&discontinuedflag=&specialCertRender=false&staticPage="
        self.driver.get(urlCreator)
        sleep(.5)

        #TABLE RENDER
        ignoreSups = ['VWR Catalog Number','Unit','Price','Quantity','Supplier No.']

        priceSearch = []
        xCompile = []

        subs = self.driver.find_elements(By.XPATH,"//table[contains(@class,'table-stack')]//tbody")
        for count in range(len(subs)):
            try:
                #print(count)
                xData = data.copy()
                vwrNew = False
                tempAttributes = data['productAttributes'].copy()
                tempProductCodes = data['productCodes'].copy()
                tempPrice = data['price'].copy()
                innerLen =len(subs[count].find_elements(By.TAG_NAME,"tr"))-1
                for inn in range(innerLen): 
                    x = subs[count].find_elements(By.TAG_NAME,"tr")[inn].find_elements(By.TAG_NAME,"td")
                    for i in x:
                        if(i.get_attribute("data-title") not in ignoreSups):
                            tempAttributes.append({'name': i.get_attribute("data-title"),'value':i.text})
                        if(i.get_attribute("data-title") == 'Supplier No.'):
                            tempProductCodes.append({'codeType':'Supplier No.','code':i.text})
                        if(i.get_attribute("data-title") == "VWR Catalog Number"):
                            tempProductCodes.append({'codeType':"Catalog Code",'code':i.text})
                            vwrNew = True
                        if(i.get_attribute("data-title") == "Unit"):
                            unitData = i.text
                        if(i.get_attribute("data-title") == "Price"):
                            tdsku = i.get_attribute("id").replace("LA","")
                            tempPrice.append({'quantity':'1','unitSize':unitData,'sku':tdsku,'currency':'','price':''})
                            priceSearch.append(tdsku)
                if(vwrNew):
                    xData['productAttributes'] = tempAttributes
                    xData['productCodes'] = tempProductCodes
                    xData['price'] = tempPrice

                    xCompile.append(xData)
                else:
                    xCompile[-1]['price'] = xCompile[-1]['price'] + tempPrice
            except Exception as e:
                print(e)


        if(priceSearch!=[]):
            urlCreator = self.baseUrl+"/store/services/pricing/json/skuPricing.jsp?skuIds="+str(','.join(priceSearch))
            self.driver.get(urlCreator)
            sleep(.5)
            self.parsePrices(xCompile)
            
            
    def main(self):
        try:
            self.logIn()
            sleep(1)
            self.driver.get(self.getLinkUrl)
            self.getCategoryLinks()
            print(f'VWR BULK: Total links category links {len(self.categoryLinks)}')
            for count,i in enumerate(self.categoryLinks):
                self.getProductLinks(i)
                
            print(len(self.productLinks))
            for links in self.productLinks:
                try:
                    self.driver.get(links)
                    sleep(1)
                    self.getProduct(links)
                except Exception as e:
                    print(e)
                    pass

            with open(self.fileName, "a") as f:
                f.write(']')
            self.driver.close()
        except Exception as e:
            print(e)
            self.driver.close()
# userName = 'nana.ali.elmogey@gmail.com'
# passwrod = 'AxiomPassword123!'
# userName = 'nana.ali.elmogey@gmail.com'
# passwrod = 'AxiomPassword123!'
# t = VwrAuthBulkSelenium('VWRBULKSELENIUM',userName, passwrod)
# t.main()