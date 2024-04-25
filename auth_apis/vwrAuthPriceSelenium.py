from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.common.exceptions import TimeoutException
import json
import re
from time import sleep


class VwrAuthPriceSelenium():
    getLinkUrl = 'https://us.vwr.com/store/product/4541052/vwr-microgrip-purple-nitrile-poly-coated-powder-freegloves'
    
    locale = 'us'
    baseUrl = 'https://'+locale+'.vwr.com'
    #'https://www.thermofisher.com/order/catalog/product/TLR102R-Q?SID=srch-srp-TLR102R-Q'
    #'https://www.thermofisher.com/order/catalog/product/991SP12?SID=srch-srp-991SP12'
    
    def __init__(self,url=None,locale=None,userName=None,password=None):
        self.userName= userName
        self.password = password
        self.driver = self.get_driver()
        self.getLinkUrl = url
        self.locale = locale
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
            compiledResult.append({'price':p['price']})
        return(compiledResult)

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
        Options.add_argument("window-size=1920x1080")
        #Options.add_argument(f"user-agent={self.customUserAgent}")
        return webdriver.Chrome(ChromeDriverManager().install(),options=Options)
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
    
    def getProduct(self):
        #MAIN PRODUCT PAEG
        try:
            productId = re.findall(r"/product/(.*?)/",self.getLinkUrl)[0]
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
        data = {
            # 'mainCat':catName,
            'URL':self.getLinkUrl,
            'productName':self.driver.find_element(By.XPATH,"//h1/*[@itemprop='name']").text,
            'productdescription':self.driver.find_element(By.XPATH,"//*[@class='product_desc_container']/div[contains(@class,'textBodyText ')]").text.split("Certifications:")[0],#html
            'productCodes':productCodes,#array of dict
            'brand':self.driver.find_element(By.XPATH,"//*[@itemprop='manufacturer']").text,
            'breadcrumb':breadcrumb, 
            'price':[], #array of dict
            'productAttributes':productList, 
            'imageURLs':str(images), 
        }
        urlCreator = self.baseUrl+"/store/services/catalog/json/stiboSpecificationsRender.jsp?productId="+str(productId)+"&catalogNumber="
        self.driver.get(urlCreator)
        sleep(1)

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
        sleep(1)

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
            sleep(1)
            returnedData = self.parsePrices(xCompile)
            return returnedData
            
            
    def main(self):
        try:
            self.logIn()
            self.driver.get(self.getLinkUrl)
            sleep(1)
            returnedData = self.getProduct()
            self.driver.close()
            print(returnedData)
            print(len(returnedData))
            return returnedData
        except Exception as e:
            print(e)
            self.driver.close()
            return []
# userName = 'nana.ali.elmogey@gmail.com'
# passwrod = 'AxiomPassword123!'
# t = VwrAuthPriceSelenium('https://us.vwr.com/store/product/8876764/herbarium-paste',
# userName, passwrod)

# result = t.main()
# for i in result:
#     print(i)