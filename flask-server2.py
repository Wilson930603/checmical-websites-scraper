from unicodedata import name
from xml.dom.expatbuilder import parseString
import crochet
from scrapy.utils.project import get_project_settings
crochet.setup()  # initialize crochet before further imports

from flask import Flask, jsonify, request, abort
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher

from latest_user_agents import get_latest_user_agents, get_random_user_agent

import os, sys
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.path.dirname(__file__), "auth_apis"))
from flasks.spiders import (
    vwr_page, vwr_price,
    sigmaaldrich_page, sigmaaldrich_price,
    faust_page, faust_price,
    thermofisher_page, thermofisher_price,
    fishersci_page, fishersci_price,
)
from auth_apis import (
    vwrAuthPageSelenium, vwrAuthPriceSelenium,
    sigmaaldrichAuthPriceSelenium, sigmaaldrichAuthPageSelenium,
    faust_auth_page, faust_auth_price,
    thermofisherAuthPageSelenium, thermofisherAuthPriceSelenium,
)
import json
import re


app = Flask(__name__)
output_data = []
crawl_runner = CrawlerRunner(get_project_settings())


@app.route("/page", methods=['POST'])
def page():
    try:
        rawJson = request.get_json()
        sitename = rawJson.get('Sitename', '').lower()
        url = rawJson.get('URL')
        username = rawJson.get('Username')
        password = rawJson.get('Password')
    except:
        rawJson = json.loads(request.get_data())
        sitename = rawJson['Sitename'].lower()
        url = rawJson['URL']
        username = rawJson['Username']
        password = rawJson['Password']
    print(url)
    if username and password:
        if sitename == "vwr":
            regex = 'uk'
            try:
                regex = re.findall(r"https://(.*?)\.vwr\.com",url)[0]
            except:
                pass
            vwr = vwrAuthPageSelenium.VwrAuthPageSelenium(url,regex,username,password)
            vwrResults = vwr.main()
            return jsonify(vwrResults)
        elif sitename == "thermofisher":
            thermoResults = []
            thermofisherPage = thermofisherAuthPageSelenium.ThermofisherAuthPageSelenium(url,username,password)
            for i in thermofisherPage.main():
                thermoResults.append(i)
            return jsonify(thermoResults)
        elif sitename == 'sigmaaldrich':
            sigmaResults = []
            sigmaldrichPage = sigmaaldrichAuthPageSelenium.SigmaaldrichAuthPageSelenium(url,username,password)
            sigmaResults = sigmaldrichPage.main()
            return jsonify(sigmaResults)
    scrape_with_crochet("page", sitename, url, username, password)
    return jsonify(output_data)


@app.route("/price", methods=['POST'])
def price():
    try:
        rawJson = request.get_json()
        sitename = rawJson.get('Sitename', '').lower()
        url = rawJson.get('URL')
        username = rawJson.get('Username')
        password = rawJson.get('Password')
    except:
        rawJson = json.loads(request.get_data())
        sitename = rawJson['Sitename'].lower()
        url = rawJson['URL']
        username = rawJson['Username']
        password = rawJson['Password']
    if username and password:
        if sitename == "vwr":
            regex = 'uk'
            try:
                regex = re.findall(r"https://(.*?)\.vwr\.com",url)[0]
            except:
                pass
            vwr = vwrAuthPriceSelenium.VwrAuthPriceSelenium(url,regex,username,password)
            vwrResults = vwr.main()
            return jsonify(vwrResults)
        elif sitename == "thermofisher":
            thermoResults = []
            thermofisherPrice = thermofisherAuthPriceSelenium.thermofisherAuthPrice(url,username,password)
            for i in thermofisherPrice.main():
                thermoResults.append(i)
            return jsonify(thermoResults)
        elif sitename == 'sigmaaldrich':
            sigmaResults = []
            sigmaldrichPrice = sigmaaldrichAuthPriceSelenium.SigmaaldrichAuthPriceSelenium(url,username,password)
            sigmaResults = sigmaldrichPrice.main()
            return jsonify(sigmaResults)
    scrape_with_crochet("price", sitename, url, username, password)
    return jsonify(output_data)


@crochet.wait_for(timeout=90.0)
def scrape_with_crochet(mode, sitename, url, username, password):
    global output_data
    output_data = []

    dispatcher.connect(_crawler_result, signal=signals.item_scraped)
    sitename = sitename.lower()
    if mode == 'page':
        print("PAGE" + " " + sitename)
        if sitename == 'vwr':
            regex = 'uk'
            try:
                regex = re.findall(r"https://(.*?)\.vwr\.com",url)[0]
            except:
                pass
            eventual = crawl_runner.crawl(
                vwr_page.vwrPageSpider, start_urls=[url], locale=regex)
        elif sitename == 'sigmaaldrich':
            # if username and password:
            #     eventual = crawl_runner.crawl(
            #         sigmaaldrich_auth_page.sigmaaldrichAuthPageSpider, start_urls=[url], userName=username, passWord=password)
            # else:
            eventual = crawl_runner.crawl(
                sigmaaldrich_page.sigmaaldrichPageSpider, start_urls=[url])
        elif sitename == 'faust':
            if username and password:
                eventual = crawl_runner.crawl(
                    faust_auth_page.faustAuthPageSpider, start_urls=[url], userName=username, password=password)
            else:
                eventual = crawl_runner.crawl(
                    faust_page.faustPageSpider, start_urls=[url])
        elif sitename == 'fishersci':
            eventual = crawl_runner.crawl(
                fishersci_page.fishersciPageSpider, start_urls=['https://www.fishersci.co.uk'], daPage=url)
        elif sitename == 'thermofisher':
            eventual = crawl_runner.crawl(
                thermofisher_page.thermofisherPageSpider, start_urls=['https://www.thermofisher.com'], daPage=url)

        return eventual
    elif mode == 'price':
        print("PRICE" + " " + sitename)
        if sitename == 'vwr':
            regex = 'uk'
            try:
                regex = re.findall(r"https://(.*?)\.vwr\.com",url)[0]
            except:
                pass
            eventual = crawl_runner.crawl(
                vwr_price.vwrPriceSpider, start_urls=[url], locale=regex)

        elif sitename == 'sigmaaldrich':
            # if username and password:
            #     eventual = crawl_runner.crawl(
            #         sigmaaldrich_auth_price.sigmaaldrichAuthPriceSpider, start_urls=[url], userName=username, passWord=password)
            # else:
            eventual = crawl_runner.crawl(
                sigmaaldrich_price.sigmaaldrichPriceSpider, start_urls=[url])

        elif sitename == 'faust':
            # if('UID' in url):
            #     try:
            #         url = re.findall(r"(.*?)\?UID",url)[0]
            #         print(url)
            #     except Exception as e:print(e)
            if username and password:
                eventual = crawl_runner.crawl(
                    faust_auth_price.faustAuthPriceSpider, start_urls=[url], userName=username, password=password)
            else:
                eventual = crawl_runner.crawl(
                    faust_price.faustPriceSpider, start_urls=[url])

        elif sitename == 'fishersci':
            eventual = crawl_runner.crawl(
                fishersci_price.fishersciPriceSpider, start_urls=['https://www.fishersci.co.uk'], daPage=url)
        elif sitename == 'thermofisher':
            eventual = crawl_runner.crawl(
                thermofisher_price.thermofisherPriceSpider, start_urls=['https://www.thermofisher.com'], daPage=url)

        return eventual


def _crawler_result(item, response, spider):
    global output_data
    """
    We're using dict() to decode the items.
    Ideally this should be done using a proper export pipeline.
    """
    # print(item)
    output_data.append(dict(item))
    # output_data = item


if __name__ == '__main__':
    app.run('0.0.0.0', 8080, debug=True)
