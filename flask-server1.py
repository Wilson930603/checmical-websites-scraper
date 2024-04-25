from time import sleep
from xml.dom.expatbuilder import parseString
import crochet
from waitress import serve
from scrapy.utils.project import get_project_settings
crochet.setup()  # initialize crochet before further imports

from flask import Flask, request
from scrapy import signals
from scrapy.crawler import CrawlerRunner
import os, sys
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.path.dirname(__file__), "auth_apis"))

from flasks.spiders import (
    sigmaaldrich_bulk,
    vwr_bulk,
    faust_bulk,
    fishersci_bulk,
    thermofisher_bulk,
)
from auth_apis import (
    sigmaaldrichAuthBulkSelenium,
    vwrAuthBulkSelenium,
    faust_auth_bulk,
    thermofisherAuthBulkSelenium,
)
import json
import gc
import threading


app = Flask(__name__)
output_data = []
# crawl_runner = CrawlerRunner(get_project_settings())
# crawl_runner = CrawlerRunner(get_project_settings()) if you want to apply settings.py
vwr_scrape_in_progress = False
vwr_scrape_complete = False
sigma_scrape_in_progress = False
sigma_scrape_complete = False
faust_scrape_in_progress = False
faust_scrape_complete = False
fishersci_scrape_in_progress = False
fishersci_scrape_complete = False
thermofisher_scrape_in_progress = False
thermofisher_scrape_complete = False
####
scrape_complete = False
scrape_in_progress = False

def runVwrBulk(filename,username,password):

    t = vwrAuthBulkSelenium.VwrAuthBulkSelenium(filename,username, password)
    t.main()
    finished_scrape_vwr(null="")
def runThermofisherBulk(filename,username,password):
    t = thermofisherAuthBulkSelenium.ThermofisherAuthBulkSelenium(filename,username, password)
    t.main()
    finished_scrape_thermofisher(null="")
def runSigmaldrichBulk(filename,locale,lang,username,password):
    t = sigmaaldrichAuthBulkSelenium.SigmaaldrichAuthBulkSelenium(filename,locale,lang,username, password)
    t.main()    
    finished_scrape_sigmaaldrich(null="")

@app.route("/status", methods=['GET','POST'])
def status():
    global scrape_complete, sigma_scrape_complete, vwr_scrape_complete,faust_scrape_complete,fishersci_scrape_complete,thermofisher_scrape_complete
    global scrape_in_progress, sigma_scrape_in_progress, vwr_scrape_in_progress, faust_scrape_in_progress, fishersci_scrape_in_progress,thermofisher_scrape_in_progress
    statusText = ''
    if(sigma_scrape_in_progress):
        statusText+= "Sigmaaldrich is still running."+"\n"
    elif(not sigma_scrape_in_progress and sigma_scrape_complete):
        statusText+= "Sigmaaldrich has been finished."+"\n"
    else:
        statusText+= "Sigmaaldrich is Idle."+"\n"

    if(vwr_scrape_in_progress):
        statusText+= "VWR is still running."+"\n"
    elif(not vwr_scrape_in_progress and vwr_scrape_complete):
        statusText+= "VWR has been finished."+"\n"
    else:
        statusText+= "VWR is Idle."+"\n"

    if(faust_scrape_in_progress):
        statusText+= "Faust is still running."+"\n"
    elif(not faust_scrape_in_progress and faust_scrape_complete):
        statusText+= "Faust has been finished."+"\n"
    else:
        statusText+= "Faust is Idle."+"\n"

    if(fishersci_scrape_in_progress):
        statusText+= "Fishersci is still running."+"\n"
    elif(not fishersci_scrape_in_progress and fishersci_scrape_complete):
        statusText+= "Fishersci has been finished."+"\n"
    else:
        statusText+= "Fishersci is Idle."+"\n"

    if(thermofisher_scrape_in_progress):
        statusText+= "Thermofisher is still running."+"\n"
    elif(not thermofisher_scrape_in_progress and thermofisher_scrape_complete):
        statusText+= "Thermofisher has been finished."+"\n"
    else:
        statusText+= "Thermofisher is Idle."+"\n"

    return statusText


@app.route("/bulk", methods=['POST'])
def bulk():
    global scrape_complete, sigma_scrape_complete, vwr_scrape_complete,faust_scrape_complete,fishersci_scrape_complete,thermofisher_scrape_complete
    global scrape_in_progress, sigma_scrape_in_progress, vwr_scrape_in_progress, faust_scrape_in_progress, fishersci_scrape_in_progress,thermofisher_scrape_in_progress
    country = 'US'
    language = 'EN'
    username = ''
    password = ''
    try:
        rawJson = request.get_json()
        sitename = rawJson.get('Sitename', '').lower()
        try:
            country = rawJson.get('Country').upper()
        except:pass
        try:
            language = rawJson.get('Language').lower()
        except:pass
        filename = rawJson.get('Filename').replace(".json","")
        username = rawJson.get('Username')
        password = rawJson.get('Password')
    except: 
        try:
            rawJson = json.loads(request.get_data())
            sitename = rawJson['Sitename'].lower()
            try:
                country = rawJson['Country'].upper()
            except:pass
            try:
                language = rawJson['Language'].lower()
            except:pass
            filename = rawJson['Filename'].replace(".json","")
            username = rawJson['Username']
            password = rawJson['Password']
        except:
            return {'POST_ERROR' : 'Please check post data .. '}
    print(sitename)
    if sitename == 'sigmaaldrich':
        if not sigma_scrape_in_progress:
            if username and password:
                t = threading.Thread(target=runSigmaldrichBulk,args=(filename,country,language,username,password,))
                t.start()
                check = {"Running": "Scraping VWR AUTH BULK Started"}
                sigma_scrape_in_progress = True
                sigma_scrape_complete = False
                return check

            sigma_scrape_in_progress = True
            sigma_scrape_complete = False
            scrape_with_crochet2(sitename, country, language, filename, username, password)
        return {'Sigmaaldrich': 'scraping is still running. Please retry later.'}
    elif sitename == 'vwr':
        if not vwr_scrape_in_progress:
            try:
                country = country.lower()
            except:
                pass

            if username and password:
                t = threading.Thread(target=runVwrBulk,args=(filename,username,password,))
                t.start()
                check = {"Running": "Scraping VWR AUTH BULK Started"}
                vwr_scrape_in_progress = True
                vwr_scrape_complete = False                
                return check

            vwr_scrape_in_progress = True
            vwr_scrape_complete = False
            scrape_with_crochet2(sitename, country, language, filename, username, password)
        return {'VWR ': 'Scraping is still running. Please retry later.'}
    elif sitename == 'faust':
        if not faust_scrape_in_progress:
            try:
                country = country.lower()
            except:
                pass
            faust_scrape_in_progress = True
            faust_scrape_complete = False
            scrape_with_crochet2(sitename, country, language, filename, username, password)
        return {'faust': 'scraping is still running. Please retry later.'}
    elif sitename == 'fishersci':
        if not fishersci_scrape_in_progress:
            try:
                country=country.lower()
            except:pass
            fishersci_scrape_in_progress = True
            fishersci_scrape_complete = False
            scrape_with_crochet2(sitename, country, language, filename)
        return {'fishersci':  'scraping is still running. Please retry later.'}
    elif sitename == 'thermofisher':
        if not thermofisher_scrape_in_progress:
            try:
                country = country.lower()
            except:
                pass
            if username and password:
                t = threading.Thread(target=runThermofisherBulk,args=(filename,username,password,))
                t.start()
                check = {"Running": "Scraping THERMOFISHER BULK Started"}
                thermofisher_scrape_in_progress = True
                thermofisher_scrape_complete = False
                return check
            thermofisher_scrape_in_progress = True
            thermofisher_scrape_complete = False
            scrape_with_crochet2(sitename, country, language, filename, username, password)
        return {'thermofisher':  'scraping is still running. Please retry later.'}
    else:
        return {'error': 'Sitename is wrong. '}


##########################################
@crochet.run_in_reactor
def scrape_with_crochet2(sitename, country, language, filename, username=None, password=None):
    s = get_project_settings()
    s.update({
        'ITEM_PIPELINES':{
            'flasks.pipelines.CSVPipeline': 300,
        },
        # 'ROTATING_PROXY_LIST_PATH':'proxy.txt',
        'DOWNLOADER_MIDDLEWARES':{
            'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
            'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
        },
        'CONCURRENT_REQUESTS_PER_IP':1,
        'DOWNLOAD_TIMEOUT':20,
    })

    crawl_runner = CrawlerRunner(s)
    # print(s)
    # print(s.items)
    if sitename == 'vwr':
        # if username and password:
        #     eventual = crawl_runner.crawl(vwr_auth_bulk.vwrAuthBulkSpider, filename=filename, userName=username, passWord=password)
        # else:
        eventual = crawl_runner.crawl(vwr_bulk.vwrBulkSpider, filename=filename)
        eventual.addCallback(finished_scrape_vwr)
    elif sitename == 'sigmaaldrich':
        # if username and password:
        #     eventual2 = crawl_runner.crawl(sigmaaldrich_auth_bulk.sigmaaldrichAuthBulkSpider, locale=country, lang=language, filename=filename, userName=username, passWord=password)
        # else:
        eventual2 = crawl_runner.crawl(sigmaaldrich_bulk.sigmaaldrichBulkSpider, locale=country, lang=language, filename=filename)
        eventual2.addCallback(finished_scrape_sigmaaldrich)
    elif sitename == 'faust':
        if username and password:
            eventual3 = crawl_runner.crawl(faust_auth_bulk.faustAuthBulkSpider, locale=country, lang=language.lower(), filename=filename, userName=username, password=password)
        else:
            eventual3 = crawl_runner.crawl(faust_bulk.faustBulkSpider, locale=country, lang=language.lower(), filename=filename)
        eventual3.addCallback(finished_scrape_faust)
    elif sitename == 'fishersci':
        eventual4 = crawl_runner.crawl(fishersci_bulk.fishersciBulkSpider, locale=country.lower(), lang=language.lower(), filename=filename)
        eventual4.addCallback(finished_scrape_fishersci)
    elif sitename == 'thermofisher':
        # if username and password:
        #     eventual5 = crawl_runner.crawl(thermofisher_auth_bulk.thermofisherAuthBulkSpider, filename=filename, userName=username, passWord=password)
        # else:
        eventual5 = crawl_runner.crawl(thermofisher_bulk.thermofisherBulkSpider, filename=filename)
        eventual5.addCallback(finished_scrape_thermofisher)


def finished_scrape_vwr(null):
    global vwr_scrape_complete,vwr_scrape_in_progress
    vwr_scrape_complete = True
    vwr_scrape_in_progress = False
    print("VWR DONE")
    gc.collect()


def finished_scrape_sigmaaldrich(null):
    global sigma_scrape_complete,sigma_scrape_in_progress
    sigma_scrape_complete = True
    sigma_scrape_in_progress = False
    print("SIGMA DONE")
    gc.collect()


def finished_scrape_faust(null):
    global faust_scrape_complete,faust_scrape_in_progress
    faust_scrape_complete = True
    faust_scrape_in_progress = False
    print("faust DONE")
    gc.collect()


def finished_scrape_fishersci(null):
    global fishersci_scrape_complete,fishersci_scrape_in_progress
    fishersci_scrape_complete = True
    fishersci_scrape_in_progress = False
    print("fishersci DONE")
    gc.collect()


def finished_scrape_thermofisher(null):
    global thermofisher_scrape_complete,thermofisher_scrape_in_progress
    thermofisher_scrape_complete = True
    thermofisher_scrape_in_progress = False
    print("thermofisher DONE")
    gc.collect()


def finished_scrape(null):
    global scrape_complete,scrape_in_progress
    scrape_complete = True
    scrape_in_progress = False
    print("DONE")


if __name__=='__main__':
    # app.run('ec2-13-40-107-142.eu-west-2.compute.amazonaws.com', 8081, debug=True)
    app.run('0.0.0.0', 8081)
    # serve(app,host='0.0.0.0',port=8081)