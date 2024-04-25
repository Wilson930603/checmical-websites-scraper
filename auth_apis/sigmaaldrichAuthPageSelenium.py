from http import cookies
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import os
from selenium.webdriver.common.by import By
import json
import re
from time import sleep
from datetime import datetime
import random
class SigmaaldrichAuthPageSelenium():
    locale = 'CH'
    lang = 'en'
    getLinkUrl = "https://www.sigmaaldrich.com/GB/en/product/mm/xx1014704"

    def __init__(self,url=None,userName=None,password=None):
        self.proxyList = []
        self.usedProxy = []
        self.maxProxy = 1000

        with open("proxy.txt") as file:
            for line in file: 
                line = line.strip() #or some other preprocessing
                self.proxyList.append(line) #storing everything in memory!
        self.logFile = datetime.now().strftime("SigmadrichAuthPageSelenium_%Y_%m_%d-%I-%M-%S_%p")
        with open(f'{self.logFile}.log','w') as f:
            f.write('SIGMA AUTH PAGE SELENIUM LOGS\n')   
        self.userName= userName
        self.password = password
        self.driver = self.get_driver()
        self.getLinkUrl = url
        url = url.split('/')
        print(url)
        self.locale = url[3]
        self.lang = url[4]
        self.cookies = [{'domain': 'www.sigmaaldrich.com',
        'expiry': 4807606889,
        'httpOnly': False,
        'name': 'country',
        'path': '/',
        'sameSite': 'None',
        'secure': True,
        'value': self.locale},
        {'domain': 'www.sigmaaldrich.com',
        'expiry': 4807606889,
        'httpOnly': False,
        'name': 'language',
        'path': '/',
        'sameSite': 'None',
        'secure': True,
        'value': self.lang}
        ]
    def set_cookies(self):
        self.driver.delete_all_cookies()
        for cookie in self.cookies:
            self.driver.add_cookie(cookie)
        
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
                driver.get(f'https://www.sigmaaldrich.com/{self.locale}/en/login')
                sleep(.5)
                driver.find_element(By.XPATH,"//input[contains(@id,'userName')]").send_keys(self.userName)
                return driver
            except Exception as e:
                print(e)
                print(f'Proxy Failed: {tempProxy}, Using next proxy!')
                self.writeLogs(str(e))
                self.writeLogs(f'{i+1}) Proxy Failed: {tempProxy}, Using next proxy!\n')
                driver.close()

    def login(self):
        #self.driver.get('https://www.sigmaaldrich.com/')
        #self.set_cookies()
        #self.driver.get(self.getLinkUrl)
        #self.driver.find_element(By.XPATH,"//a[contains(@href,'/profile')]").click()
        #self.driver.get(f'https://www.sigmaaldrich.com/{self.locale}/en')
        self.driver.get(f'https://www.sigmaaldrich.com/{self.locale}/en/login')
        #self.driver.find_element(By.XPATH,"//button[contains(@id,'header-login-link')]").click()
        sleep(.5)

        self.driver.find_element(By.XPATH,"//input[contains(@id,'userName')]").send_keys(self.userName)
        self.driver.find_element(By.XPATH,"//input[contains(@id,'password')]").send_keys(self.password)
        try:
            self.driver.find_element(By.XPATH,'//button[contains(@id,"onetrust-accept-btn-handler")]').click()
        except Exception as e:
            print(e)
        self.driver.find_element(By.XPATH,"//button[contains(@id,'login-page-sign-in-button')]").click()
    def getProductLinks(self):
        self.set_cookies()
        self.driver.get(self.getLinkUrl)
        try:
            self.driver.find_element(By.XPATH,'//button[contains(@id,"onetrust-accept-btn-handler")]').click()
        except Exception as e:
            print(e)
        self.productLinks = set(link.get_attribute('href') for link in self.driver.find_elements(By.XPATH,value='//a[contains(@href,"/product/")]'))

    def getProduct(self, link):
        try:

            #self.set_cookies()
            #self.driver.get(f'https://www.sigmaaldrich.com/{self.locale}/en')
            self.driver.get(link)
            print(f'LINK: {link}')
            self.writeLogs(f'LINK SCRAPING: {link}\n')

            sleep(3)
            try:
                temp = re.findall(r"/product/([^>]*)",self.driver.current_url)[0].replace("/product/","")
                temps = temp.split("/")
            except Exception as e:
                print(e)
                print('{"status":"URL error"}')
            brandkey = temps[0]
            productkey = temps[1]
            productkey
            #yield scrapy.Request('https://www.sigmaaldrich.com/api',callback=self.parseDetail,body=rawJsonz,method='POST',headers=self.headers,meta={'mainCat':'','payLoad':payloadz,'productUrl':urlCreator},dont_filter=True)

            #Columns of price table
            columns = [col.text for col in self.driver.find_elements(By.XPATH,"//thead[contains(@class,'MuiTableHead-root')]/tr/th")]
            #Items in price table
            items = [col.text for col in self.driver.find_elements(By.XPATH,"//tbody[contains(@class,'MuiTableBody-root')]/tr/td")]
            items[-1] = items[-1].replace('','1')
            priceList = []
            sku = []
            if (len(columns) == 6):
                if len(items)>5:
                    i=0
                    while i<len(items):
                        priceList.append([{'quantity':'1','unitSize':items[i+1],'currency':''.join([i for i in items[i+4] if not i.isdigit() and i !='.' and i!=',']),'price':''.join([i for i in items[i+4] if i.isdigit() or i == ',' or i=='.'])}])
                        sku.append(items[i])
                        i+=6
                else:
                    priceList.append([{'quantity':'1','unitSize':items[1],'currency':''.join([i for i in items[3] if not i.isdigit() and i !='.' and i!=',']),'price':''.join([i for i in items[3] if i.isdigit() or i == ',' or i=='.'])}])
                    sku.append(items[0])
            elif len(columns) == 5:

            
                if len(items)>5:
                    i=0
                    while i<len(items):
                        priceList.append([{'quantity':'1','unitSize':items[i+1],'currency':''.join([i for i in items[i+3] if not i.isdigit() and i !='.' and i!=',']),'price':''.join([i for i in items[i+3] if i.isdigit() or i == ',' or i=='.'])}])
                        sku.append(items[i])
                        i+=5
                else:
                    priceList.append([{'quantity':'1','unitSize':items[1],'currency':''.join([i for i in items[3] if not i.isdigit() and i !='.' and i!=',']),'price':''.join([i for i in items[3] if i.isdigit() or i == ',' or i=='.'])}])
                    sku.append(items[0])

            #Product Name
            try:
                productName = self.driver.find_element(By.XPATH,"//span[contains(@id,'product-name')]").text
            except:
                productName = ''
            #Product sub name
            try:
                name2 = self.driver.find_element(By.XPATH,"//span[contains(@id,'product-description')]").text
            except:
                name2 = ''
            #Prodcut description
            description = ''
            try:
                #description = self.driver.find_element(By.XPATH,"//h3[contains(@class,'MuiTypography-root jss279 MuiTypography-h3')]").text
                description =" \n ".join([i.text for i in self.driver.find_elements(By.XPATH,"//div[contains(@class,'MuiTypography-root')]/span")])
            except Exception as e:
                description = ''
            #Product Codes
            productCodes = []
            try:
                synonym = self.driver.find_element(By.XPATH,"//div[contains(@class,'MuiTypography-root jss218 MuiTypography-body1')]/span").text
                productCodes.append({'codeType': 'Synonym(s)', 'codeValue': synonym})
            except:
                synonym = ""
            try:
                eClass = self.driver.find_element(By.XPATH,"//div[contains(@class,'MuiGrid-root MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-sm-6')]/span").text
                productCodes.append({'codeType': 'eCl@ss', 'codeValue': eClass})
            except:
                eClass = ""
                
            #Product Attributes
            productAttributes = []
            try:
                tempAtt = self.driver.find_elements(By.XPATH,"//div[contains(@class,'MuiGrid-root MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-md-12')]/div/div/div")
                #print(tempAtt.text)
                for count in range(0,len(tempAtt)-2,2):
                    productAttributes.append({tempAtt[count].text.strip('\n'):tempAtt[count+1].text.strip('\n')})
            except Exception as e:
                productAttributes = []
            image_Urls = ''
            try:
                image_Urls = self.driver.find_element(By.XPATH,"//img[contains(@id,'active-image')]").get_attribute("src")
                image_Urls = image_Urls.replace('medium','large')
            except:
                image_Urls = ''
            #Availabilty
            try:
                self.driver.find_element(By.XPATH,f'//span[contains(@id,"mat-num-{items[0]}-from")]').click()
                availability = self.driver.find_element(By.XPATH,'//div//div//ol//li//p').text
                sleep(0.1)
                self.driver.find_element(By.XPATH,'//button[contains(@id,"mat-avl-modal-close")]').click()
            except Exception as e:
                #print(e)
                try:
                    availability = items[2]
                except Exception as e:

                    availability = []

            #Document
            document = []
            try:
                url = self.driver.current_url.split('/')
                pt1 = url[-1]
                pt2 = url[-2]
                self.driver.find_element(By.XPATH,f'//span[contains(@id,"sds-{brandkey.upper()}{pt1.upper()}")]')

                lang = ['en','de','pt','fr','it']
                for var in lang:
                    document.append(f'https://www.sigmaaldrich.com/{self.locale}/{var}/sds/{pt2}/{pt1}')

                # sleep(0.8)
                # versions = driver.find_elements(By.XPATH,'//a[contains(@class,"MuiTypography-root MuiLink-root MuiLink-underlineNone jss648 MuiTypography-colorPrimary")]')
                # document = [ver.get_attribute("href") for ver in versions]
                # driver.find_element(By.XPATH,'//button[contains(@id,"sds-modal-close-button")]').click()
            except Exception as e:
                document = []
            try:
                productNum = self.driver.find_element(By.XPATH,'//p[contains(@id,"product-number")]').text
            except:
                productNum = ''
            data = {
                'Product_Number' : productNum,
                'SKU': sku,
                'Product_Name':productName,
                'Product_Name2':name2,
                'Product_Description':description,
                'Product_Codes': str(productCodes),
                'Product_Attributes': str(productAttributes),
                'Price':priceList,
                'Page_URL':self.driver.current_url,
                'Page_Group':'',
                'Image_URLS': image_Urls,
                'Document_URLS':document,
                'Availability':availability,
                'Breadcrumbs':''
            }
            self.writeLogs(data,True)
            return data
        except Exception as e:
            print(e)
        
        
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
            self.login()
            sleep(3)
            self.getProductLinks()
            data = []
            for count,i in enumerate(self.productLinks):
                data.append(self.getProduct(i))
                print(f'Pages scraped: {count+1}')
            self.driver.close()
            print(data)
            print(len(data))
            self.productLinks = []
            return data
        except Exception as e:
            print(e)
            self.driver.close()
# t = SigmaaldrichAuthPageSelenium('https://www.sigmaaldrich.com/CH/en/products/filtration/filter-paper','aaron.ueckermann@axiomdata.io','AxiomPassword123!')
# Data = t.main()
# print(len(Data))