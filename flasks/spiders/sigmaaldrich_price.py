import scrapy
from bs4 import BeautifulSoup as BS
import json
from datetime import datetime
import re
from urllib.parse import unquote
import html

class sigmaaldrichPriceSpider(scrapy.Spider):
    locale = 'US' #example : CZ, FR, #please check website for available locale. usually https://sigmaaldrich.com/CH/en -> meaning Locale = CH, language  = en
    lang = 'en' #example : en,de,fr,it #please check website for available language.
    ################ SETTING HERE ####################
    start_urls=["https://www.sigmaaldrich.com/CH/en/products/analytical-chemistry/analytical-chromatography/analytical-syringes"]
    name = 'sigmaaldrichPrice'
    history = []
    payload_history = []
    headers = {
            'accept':'*/*',
            # 'accept-encoding':'gzip, deflate, br',
            'accept-language':'en-US,en;q=0.9',
            # 'content-length':'1587',
            'content-type':'application/json',
            # 'cookie':'GUID=d4f421de-1ba8-4615-b845-2c56f74b8b1a|NULL|1644293236217; accessToken=9a05ee21-8894-11ec-ac6a-b54406030275; dtCookie=v_4_srv_7_sn_E039457F769D5F46159FA32B14C25F9C_perc_100000_ol_0_mul_1_app-3A49e38e2e60c8cd4b_1; akaalb_origin-alb=~op=origin_apc:APAC|~rv=4~m=APAC:0|~os=a22342633dc1bd552d693ae0b80a3fbd~id=7b7f8ef6c66369ac73637df578109f40; rxVisitor=1644293237873J5G3UB5E1E4D77TEEG7NKRTMSAJU7EBQ; _vwo_uuid_v2=DE1F334B84224FF8BA63A42CD4970E430|266605fe36663cc47b92e9e419c72717; _vis_opt_s=1%7C; _vis_opt_test_cookie=1; _vwo_uuid=DE1F334B84224FF8BA63A42CD4970E430; _vwo_ds=3%3At_0%2Ca_0%3A0%241644293240%3A20.66589637%3A%3A37_0%3A8_0%3A0; bm_mi=2BD4771933F510BFA6DB387C33FC5E1B~cvSDnW6UNTZAkXD8V4JF7g3aEG2p1BLCAU5INiDRq3nVMT6bntqAG0RNnOR7gtlrpKMOwV/ohL6sksiN7DU8eGkFRl+/YjfhObXgfwfdkKtj0vAOcghQWj9OOyT45PSniAiOy4vwH1qTHAQNBKV5VYkxPzKhzrirqTknVPcY/Sf+AoMrTNYu+r+vjjqhyqyLXsEa0Yck4v2sAWasqO4Erd0KC6Dulon63UyIkMZPS8ciAuXPQW24IMkQw8LzroUO; _gcl_au=1.1.1619279701.1644293243; _ga=GA1.2.1536947007.1644293245; _gid=GA1.2.247707242.1644293245; ak_bmsc=7DAF5619EE5296002C7A85D1B090C717~000000000000000000000000000000~YAAQJ5ZUaFZwdZp+AQAAr86D1w5nULVZ0s9c8oy2gwoBasMTjTZdODRJ2tPHcUjnTGHsCaLNO3TP8NRplNGNlfPl0hMnTfI9fKupJIC9EZFFoiOzcNuAcXycc2+a3TmOvZ5lMg3+d5I45tsDWkqrwkzfldaJZzBDDS5SqKxrB/guRKhBRMMtkYdymLG+w8FvHaCrB5lWkZsjwbDL81ghn2xobqW4i2Plz5HHGUlzZ7xE27gfj4BW1t4VPNCj/AFDxnVvI0FQf9xDJC7R0IJmF8gEoToG0S+VWsdHJQX4ain7eAfsQhyyMI4tYkbz2qX/5DEBjgH0D1Z6pIqCdDbxhIj0NCfdc2ePr5PoPNyinWVCJ/b7dH/DGy6P1JiLw+y1QEWI5vaST+SlfaR7EKmTYai/D9oPzvp6afLy2WZh0cnJhbeQ4mZFg2dxsUCcy4PJeUqDjyFKFTqUtLQnzurLEUnc9cXiyLM/ns+PRvQfM0LekJKmDJM/9B2huisHgpNn8T4Xx9vg1uAqNRvG5NkhD4SFtwm8ZA==; JabmoSP0ses.5e8a=*; mdLogger=false; kampyle_userid=4d75-b6ff-353e-808f-7659-fc67-2121-98d4; kampyleUserSession=1644293248922; kampyleUserSessionsCount=1; kampyleUserPercentile=58.107908382283526; country=CH; language=en; _vis_opt_exp_61_combi=2; _vis_opt_exp_105_combi=2; BVBRANDID=48b10161-1fa1-4544-a0c8-9ff6ffd6a5df; BVImplmain_site=15557; _vis_opt_exp_105_goal_1=1; _vis_opt_exp_61_goal_1=1; _dc_gtm_UA-51006100-1=1; kampyleSessionPageCounter=22; _gat_UA-51006100-1=1; _uetsid=9f0540a0889411ec9ad071cf78b7cd2f; _uetvid=9f05bc70889411ec83a65732512fd164; JabmoSP0id.5e8a=59d3b9c2-ee05-4644-8388-0acea5afe4b5.1644293245.1.1644295707.1644293245.11d63c52-8f76-497c-bbf5-457ae3d6edff; bm_sv=6960EC7532C1826658B4F00B2866BC46~He4Ei0G3nJwxDa9ODmZ3ZaR2Ox6Ojzpl82mhDgSsXKvNRZoQMaUYddx7YDgffzS+MM7jnYP3y7sqz68oC1nqvRHizKULQ+6HPcNlhG6U4wVC2lkBi2brD3wPii4PSbqqiQZ3m9+7sh+8V2lndmRyQ5AA/LXursoB/XbwTv45+RM=; dtLatC=4; _vwo_sn=0%3A26%3A%3A%3A1; rxvt=1644297511370|1644293237877; dtPC=7$295217395_101h44vAHJMPIAOVAJPFSMEBBOWHMUFSVHBUEDR-0e0',
            # 'origin':'https://www.sigmaaldrich.com',
            # 'referer':'https://www.sigmaaldrich.com/CH/en/products/analytical-chemistry/analytical-chromatography/analytical-syringes?country=CH&language=en&cmsRoute=products&cmsRoute=analytical-chemistry&cmsRoute=analytical-chromatography&cmsRoute=analytical-syringes&page=3',
            'sec-ch-ua':'" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'sec-ch-ua-mobile':'?0',
            'sec-ch-ua-platform':'"Windows"',
            'sec-fetch-dest':'empty',
            'sec-fetch-mode':'cors',
            'sec-fetch-site':'same-origin',
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
            # 'x-dtpc':'7$295217395_101h33vAHJMPIAOVAJPFSMEBBOWHMUFSVHBUEDR-0e0',
            # 'x-dtreferer':'https://www.sigmaaldrich.com/CH/en/products/analytical-chemistry/analytical-chromatography/analytical-syringes?country=CH&language=en&cmsRoute=products&cmsRoute=analytical-chemistry&cmsRoute=analytical-chromatography&cmsRoute=analytical-syringes&page=2',
            # 'x-gql-access-token':'9a05ee21-8894-11ec-ac6a-b54406030275',
            'x-gql-country':locale,
            # 'x-gql-guid':'GA1.2.1536947007.1644293245',
            'x-gql-language':lang,
            'x-gql-operation-name':'CategoryProductSearch',
        }
    headers_price = {
            'accept':'*/*',
            # 'accept-encoding':'gzip, deflate, br',
            'accept-language':'en-US,en;q=0.9',
            # 'content-length':'1587',
            'content-type':'application/json',
            # 'cookie':'GUID=d4f421de-1ba8-4615-b845-2c56f74b8b1a|NULL|1644293236217; accessToken=9a05ee21-8894-11ec-ac6a-b54406030275; dtCookie=v_4_srv_7_sn_E039457F769D5F46159FA32B14C25F9C_perc_100000_ol_0_mul_1_app-3A49e38e2e60c8cd4b_1; akaalb_origin-alb=~op=origin_apc:APAC|~rv=4~m=APAC:0|~os=a22342633dc1bd552d693ae0b80a3fbd~id=7b7f8ef6c66369ac73637df578109f40; rxVisitor=1644293237873J5G3UB5E1E4D77TEEG7NKRTMSAJU7EBQ; _vwo_uuid_v2=DE1F334B84224FF8BA63A42CD4970E430|266605fe36663cc47b92e9e419c72717; _vis_opt_s=1%7C; _vis_opt_test_cookie=1; _vwo_uuid=DE1F334B84224FF8BA63A42CD4970E430; _vwo_ds=3%3At_0%2Ca_0%3A0%241644293240%3A20.66589637%3A%3A37_0%3A8_0%3A0; bm_mi=2BD4771933F510BFA6DB387C33FC5E1B~cvSDnW6UNTZAkXD8V4JF7g3aEG2p1BLCAU5INiDRq3nVMT6bntqAG0RNnOR7gtlrpKMOwV/ohL6sksiN7DU8eGkFRl+/YjfhObXgfwfdkKtj0vAOcghQWj9OOyT45PSniAiOy4vwH1qTHAQNBKV5VYkxPzKhzrirqTknVPcY/Sf+AoMrTNYu+r+vjjqhyqyLXsEa0Yck4v2sAWasqO4Erd0KC6Dulon63UyIkMZPS8ciAuXPQW24IMkQw8LzroUO; _gcl_au=1.1.1619279701.1644293243; _ga=GA1.2.1536947007.1644293245; _gid=GA1.2.247707242.1644293245; ak_bmsc=7DAF5619EE5296002C7A85D1B090C717~000000000000000000000000000000~YAAQJ5ZUaFZwdZp+AQAAr86D1w5nULVZ0s9c8oy2gwoBasMTjTZdODRJ2tPHcUjnTGHsCaLNO3TP8NRplNGNlfPl0hMnTfI9fKupJIC9EZFFoiOzcNuAcXycc2+a3TmOvZ5lMg3+d5I45tsDWkqrwkzfldaJZzBDDS5SqKxrB/guRKhBRMMtkYdymLG+w8FvHaCrB5lWkZsjwbDL81ghn2xobqW4i2Plz5HHGUlzZ7xE27gfj4BW1t4VPNCj/AFDxnVvI0FQf9xDJC7R0IJmF8gEoToG0S+VWsdHJQX4ain7eAfsQhyyMI4tYkbz2qX/5DEBjgH0D1Z6pIqCdDbxhIj0NCfdc2ePr5PoPNyinWVCJ/b7dH/DGy6P1JiLw+y1QEWI5vaST+SlfaR7EKmTYai/D9oPzvp6afLy2WZh0cnJhbeQ4mZFg2dxsUCcy4PJeUqDjyFKFTqUtLQnzurLEUnc9cXiyLM/ns+PRvQfM0LekJKmDJM/9B2huisHgpNn8T4Xx9vg1uAqNRvG5NkhD4SFtwm8ZA==; JabmoSP0ses.5e8a=*; mdLogger=false; kampyle_userid=4d75-b6ff-353e-808f-7659-fc67-2121-98d4; kampyleUserSession=1644293248922; kampyleUserSessionsCount=1; kampyleUserPercentile=58.107908382283526; country=CH; language=en; _vis_opt_exp_61_combi=2; _vis_opt_exp_105_combi=2; BVBRANDID=48b10161-1fa1-4544-a0c8-9ff6ffd6a5df; BVImplmain_site=15557; _vis_opt_exp_105_goal_1=1; _vis_opt_exp_61_goal_1=1; _dc_gtm_UA-51006100-1=1; kampyleSessionPageCounter=22; _gat_UA-51006100-1=1; _uetsid=9f0540a0889411ec9ad071cf78b7cd2f; _uetvid=9f05bc70889411ec83a65732512fd164; JabmoSP0id.5e8a=59d3b9c2-ee05-4644-8388-0acea5afe4b5.1644293245.1.1644295707.1644293245.11d63c52-8f76-497c-bbf5-457ae3d6edff; bm_sv=6960EC7532C1826658B4F00B2866BC46~He4Ei0G3nJwxDa9ODmZ3ZaR2Ox6Ojzpl82mhDgSsXKvNRZoQMaUYddx7YDgffzS+MM7jnYP3y7sqz68oC1nqvRHizKULQ+6HPcNlhG6U4wVC2lkBi2brD3wPii4PSbqqiQZ3m9+7sh+8V2lndmRyQ5AA/LXursoB/XbwTv45+RM=; dtLatC=4; _vwo_sn=0%3A26%3A%3A%3A1; rxvt=1644297511370|1644293237877; dtPC=7$295217395_101h44vAHJMPIAOVAJPFSMEBBOWHMUFSVHBUEDR-0e0',
            # 'origin':'https://www.sigmaaldrich.com',
            # 'referer':'https://www.sigmaaldrich.com/CH/en/products/analytical-chemistry/analytical-chromatography/analytical-syringes?country=CH&language=en&cmsRoute=products&cmsRoute=analytical-chemistry&cmsRoute=analytical-chromatography&cmsRoute=analytical-syringes&page=3',
            'sec-ch-ua':'" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'sec-ch-ua-mobile':'?0',
            'sec-ch-ua-platform':'"Windows"',
            'sec-fetch-dest':'empty',
            'sec-fetch-mode':'cors',
            'sec-fetch-site':'same-origin',
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
            # 'x-dtpc':'7$295217395_101h33vAHJMPIAOVAJPFSMEBBOWHMUFSVHBUEDR-0e0',
            # 'x-dtreferer':'https://www.sigmaaldrich.com/CH/en/products/analytical-chemistry/analytical-chromatography/analytical-syringes?country=CH&language=en&cmsRoute=products&cmsRoute=analytical-chemistry&cmsRoute=analytical-chromatography&cmsRoute=analytical-syringes&page=2',
            'x-gql-access-token':'1badb8f0-8894-11ec-809f-ddefbdce6cad',
            'x-gql-country':locale,
            # 'x-gql-guid':'GA1.2.1536947007.1644293245',
            'x-gql-language':lang,
            'x-gql-operation-name':'PricingAndAvailability',
        }

    def parse(self, response):
        baseUrl = response.url
        if('/products/' in baseUrl):
            yield scrapy.Request(url=baseUrl,callback=self.parseCategories,headers=self.headers,meta={'mainCat':''},dont_filter=True)
        else:
            try:
                temp = re.findall(r"/product/([^>]*)",baseUrl)[0].replace("/product/","")
                temps = temp.split("/")
            except Exception as e:
                print(e)
                return '{"status":"URL error"}'
            brandkey = temps[0]
            productkey = temps[1]
            payloadz = '{"operationName":"ProductDetail","variables":{"brandKey":"'+brandkey+'","productKey":"'+str(productkey)+'","catalogType":"sial"},"query":"query ProductDetail($brandKey: String!, $productKey: String!, $catalogType: CatalogType, $orgId: String) {\n  getProductDetail(input: {brandKey: $brandKey, productKey: $productKey, catalogType: $catalogType, orgId: $orgId}) {\n    ...ProductDetail\n    __typename\n  }\n}\n\nfragment ProductDetail on Product {\n  id\n  productNumber\n  productKey\n  erpProductKey\n  isSial\n  substance {\n    id\n    __typename\n  }\n  brand {\n    key\n    erpKey\n    name\n    logo {\n      altText\n      smallUrl\n      mediumUrl\n      largeUrl\n      __typename\n    }\n    cells {\n      altText\n      smallUrl\n      mediumUrl\n      largeUrl\n      __typename\n    }\n    color\n    __typename\n  }\n  aliases {\n    key\n    value\n    label\n    __typename\n  }\n  name\n  description\n  descriptions {\n    label\n    values\n    __typename\n  }\n  molecularWeight\n  empiricalFormula\n  linearFormula\n  casNumber\n  images {\n    altText\n    label\n    smallUrl\n    mediumUrl\n    largeUrl\n    __typename\n  }\n  synonyms\n  attributes {\n    key\n    label\n    values\n    __typename\n  }\n  materialIds\n  compliance {\n    key\n    label\n    value\n    images {\n      altText\n      smallUrl\n      mediumUrl\n      largeUrl\n      __typename\n    }\n    __typename\n  }\n  browserMetadata {\n    title\n    description\n    keywords\n    __typename\n  }\n  sdsPnoKey\n  faqs {\n    question\n    answer\n    __typename\n  }\n  peerPapers {\n    ...PaperDetails\n    __typename\n  }\n  links {\n    label\n    key\n    anchorTag\n    image\n    __typename\n  }\n  popularDocuments {\n    label\n    url\n    __typename\n  }\n  features\n  paMessage\n  catalogId\n  components {\n    kitOnly {\n      value\n      pId\n      pno\n      brand\n      erpBrandKey\n      erpPnoKey\n      __typename\n    }\n    kitSoldSeparate {\n      value\n      pId\n      pno\n      brand\n      erpBrandKey\n      erpPnoKey\n      __typename\n    }\n    analyte {\n      value\n      pId\n      __typename\n    }\n    solvent {\n      value\n      pId\n      __typename\n    }\n    bulletin {\n      value\n      pId\n      __typename\n    }\n    __typename\n  }\n  specificationSheet {\n    url\n    text\n    __typename\n  }\n  substanceCount\n  productCategories {\n    category\n    url\n    __typename\n  }\n  relatedProducts {\n    type\n    productId\n    __typename\n  }\n  type\n  customPdpId\n  protocolsAndArticles {\n    protocols {\n      ...ProtocolArticleDocument\n      __typename\n    }\n    articles {\n      ...ProtocolArticleDocument\n      __typename\n    }\n    relatedContent {\n      ...ProtocolArticleDocument\n      __typename\n    }\n    __typename\n  }\n  productRating {\n    ratingEnabled\n    __typename\n  }\n  __typename\n}\n\nfragment ProtocolArticleDocument on ProtocolArticleDocument {\n  id\n  title\n  text\n  url\n  contentType\n  __typename\n}\n\nfragment PaperDetails on Papers {\n  count\n  papers {\n    id\n    abstract\n    title\n    authors\n    date\n    pubMedId\n    journalName\n    volume\n    issue\n    startPage\n    endPage\n    __typename\n  }\n  __typename\n}\n"}'
            rawJsonz = json.loads(payloadz,strict=False)
            rawJsonz = json.dumps(rawJsonz)
            urlCreator = 'https://www.sigmaaldrich.com/'+self.locale+"/"+self.lang+"/product/"+brandkey.lower()+"/"+productkey.lower()
            yield scrapy.Request('https://www.sigmaaldrich.com/api',callback=self.parseDetail,body=rawJsonz,method='POST',headers=self.headers,meta={'mainCat':'','payLoad':payloadz,'productUrl':urlCreator},dont_filter=True)

        # baseUrl = response.url
        # rawText = response.xpath("//*[@id='__NEXT_DATA__']/text()").get()
        # rawJson = json.loads(rawText)
        
        # urlList = []
        # ### URL category generator ###
        # categories = rawJson['props']['apolloState']
        # for catKey,catVakye in categories.items():
        #     try:
        #         if(categories[catKey]['__typename']=='AemTopNavItem'):
        #             isMenu = True
        #             try:
        #                 isMenu = categories[catKey]['menuItem']
        #             except:pass
        #             if(not isMenu):
        #                 title = categories[catKey]['title']
        #                 url = categories[catKey]['url']
        #                 if('/products/' in url):
        #                     print(title)
        #                     urlCreator = 'https://www.sigmaaldrich.com'+url
        #                     urlCreator = urlCreator.replace("/EN/us/EN/us","/EN/us")
        #                     self.fileReport.write("crawl - "+urlCreator+"\n")
        #                     self.fileReport.flush()
        #                     yield scrapy.Request(url=urlCreator,callback=self.parseCategories,headers=self.headers,meta={'mainCat':title})

        #     except Exception as e: pass

    def parseCategories(self,response):
        baseUrl = response.url
        # print(baseUrl)
        mainCat = response.meta['mainCat']
        rawText = response.xpath("//*[@id='__NEXT_DATA__']/text()").get()
        # print(rawText)
        try:
            facets = []
            facetSet = []
            rawJson = json.loads(rawText)['props']['pageProps'][':items']['root'][':items']
            try:

                for key,value in rawJson['topcontainer'][':items'].items():
                    if('categorysearchresult' in key):
                        facets = rawJson['topcontainer'][':items'][key]['facets']
                        facetSet = rawJson['topcontainer'][':items'][key]['facetSet']
                        break
            except:

                try:
                    for key,value in rawJson['middlecontainer'][':items'].items():
                        if('categorysearchresult' in key):
                            facets = rawJson['middlecontainer'][':items'][key]['facets']
                            facetSet = rawJson['middlecontainer'][':items'][key]['facetSet']
                            break
                except:
                    for key,value in rawJson['bottomcontainer'][':items'].items():
                        if('categorysearchresult' in key):
                            facets = rawJson['bottomcontainer'][':items'][key]['facets']
                            facetSet = rawJson['bottomcontainer'][':items'][key]['facetSet']
                            break

            ########################### payloadCreator
            facetDictList = []
            for facet in facets:
                temp = facet.split(":")
                if(any(temp[0] in d['key'] for d in facetDictList)):
                    for d in facetDictList:
                        if(temp[0] == d['key']):
                            d['options'].append(temp[1])
                else:
                    temp = {'key':temp[0],'options':[temp[1]]}
                    facetDictList.append(temp)

            a = str(facetDictList).replace("'",'"')
            b = str(facetSet).replace("'",'"')
            payload = '{"operationName":"CategoryProductSearch","variables":{"searchTerm":null,"page":1,"perPage":20,"sort":"relevance","selectedFacets":'+a+',"facetSet":'+b+'},"query":"query CategoryProductSearch($searchTerm: String, $page: Int!, $perPage: Int!, $sort: Sort, $selectedFacets: [FacetInput!], $facetSet: [String]) {\n  getProductSearchResults(input: {searchTerm: $searchTerm, pagination: {page: $page, perPage: $perPage}, sort: $sort, group: product, facets: $selectedFacets, facetSet: $facetSet}) {\n    ...CategoryProductSearchFields\n    __typename\n  }\n}\n\nfragment CategoryProductSearchFields on ProductSearchResults {\n  metadata {\n    itemCount\n    page\n    perPage\n    numPages\n    __typename\n  }\n  items {\n    ... on Product {\n      ...CategorySubstanceProductFields\n      __typename\n    }\n    __typename\n  }\n  facets {\n    key\n    numToDisplay\n    isHidden\n    isCollapsed\n    multiSelect\n    prefix\n    options {\n      value\n      count\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CategorySubstanceProductFields on Product {\n  name\n  productNumber\n  productKey\n  attributes {\n    key\n    label\n    values\n    __typename\n  }\n  brand {\n    key\n    erpKey\n    name\n    color\n    __typename\n  }\n  description\n  paMessage\n  __typename\n}\n"}'
            rawJson = json.loads(payload,strict=False)
            rawJson = json.dumps(rawJson)

            yield scrapy.Request('https://www.sigmaaldrich.com/api',callback=self.parseProducts,body=rawJson,method='POST',headers=self.headers,meta={'mainCat':mainCat,'payLoad':payload},dont_filter=True)

        except Exception as e:
            print(e)
            self.fileReport.write("facet error - "+baseUrl+"\n")
            self.fileReport.flush()
     
    def parseProducts(self,response):
        payload = response.meta['payLoad']
        mainCat = response.meta['mainCat']
        try:
            rawJson = json.loads(response.text)
            products = rawJson['data']['getProductSearchResults']['items']
            for product in products:
                brandkey = product['brand']['key'].lower()
                productkey = product['productKey']
                payloadz = '{"operationName":"ProductDetail","variables":{"brandKey":"'+brandkey+'","productKey":"'+str(productkey)+'","catalogType":"sial"},"query":"query ProductDetail($brandKey: String!, $productKey: String!, $catalogType: CatalogType, $orgId: String) {\n  getProductDetail(input: {brandKey: $brandKey, productKey: $productKey, catalogType: $catalogType, orgId: $orgId}) {\n    ...ProductDetail\n    __typename\n  }\n}\n\nfragment ProductDetail on Product {\n  id\n  productNumber\n  productKey\n  erpProductKey\n  isSial\n  substance {\n    id\n    __typename\n  }\n  brand {\n    key\n    erpKey\n    name\n    logo {\n      altText\n      smallUrl\n      mediumUrl\n      largeUrl\n      __typename\n    }\n    cells {\n      altText\n      smallUrl\n      mediumUrl\n      largeUrl\n      __typename\n    }\n    color\n    __typename\n  }\n  aliases {\n    key\n    value\n    label\n    __typename\n  }\n  name\n  description\n  descriptions {\n    label\n    values\n    __typename\n  }\n  molecularWeight\n  empiricalFormula\n  linearFormula\n  casNumber\n  images {\n    altText\n    label\n    smallUrl\n    mediumUrl\n    largeUrl\n    __typename\n  }\n  synonyms\n  attributes {\n    key\n    label\n    values\n    __typename\n  }\n  materialIds\n  compliance {\n    key\n    label\n    value\n    images {\n      altText\n      smallUrl\n      mediumUrl\n      largeUrl\n      __typename\n    }\n    __typename\n  }\n  browserMetadata {\n    title\n    description\n    keywords\n    __typename\n  }\n  sdsPnoKey\n  faqs {\n    question\n    answer\n    __typename\n  }\n  peerPapers {\n    ...PaperDetails\n    __typename\n  }\n  links {\n    label\n    key\n    anchorTag\n    image\n    __typename\n  }\n  popularDocuments {\n    label\n    url\n    __typename\n  }\n  features\n  paMessage\n  catalogId\n  components {\n    kitOnly {\n      value\n      pId\n      pno\n      brand\n      erpBrandKey\n      erpPnoKey\n      __typename\n    }\n    kitSoldSeparate {\n      value\n      pId\n      pno\n      brand\n      erpBrandKey\n      erpPnoKey\n      __typename\n    }\n    analyte {\n      value\n      pId\n      __typename\n    }\n    solvent {\n      value\n      pId\n      __typename\n    }\n    bulletin {\n      value\n      pId\n      __typename\n    }\n    __typename\n  }\n  specificationSheet {\n    url\n    text\n    __typename\n  }\n  substanceCount\n  productCategories {\n    category\n    url\n    __typename\n  }\n  relatedProducts {\n    type\n    productId\n    __typename\n  }\n  type\n  customPdpId\n  protocolsAndArticles {\n    protocols {\n      ...ProtocolArticleDocument\n      __typename\n    }\n    articles {\n      ...ProtocolArticleDocument\n      __typename\n    }\n    relatedContent {\n      ...ProtocolArticleDocument\n      __typename\n    }\n    __typename\n  }\n  productRating {\n    ratingEnabled\n    __typename\n  }\n  __typename\n}\n\nfragment ProtocolArticleDocument on ProtocolArticleDocument {\n  id\n  title\n  text\n  url\n  contentType\n  __typename\n}\n\nfragment PaperDetails on Papers {\n  count\n  papers {\n    id\n    abstract\n    title\n    authors\n    date\n    pubMedId\n    journalName\n    volume\n    issue\n    startPage\n    endPage\n    __typename\n  }\n  __typename\n}\n"}'
                rawJsonz = json.loads(payloadz,strict=False)
                rawJsonz = json.dumps(rawJsonz)
                urlCreator = 'https://www.sigmaaldrich.com/'+self.locale+"/"+self.lang+"/product/"+product['brand']['key'].lower()+"/"+product['productKey']

                yield scrapy.Request('https://www.sigmaaldrich.com/api',callback=self.parseDetail,body=rawJsonz,method='POST',headers=self.headers,meta={'mainCat':mainCat,'payLoad':payloadz,'productUrl':urlCreator},dont_filter=True)


            # if(len(products)==20):

            #     try:
            #         pageNow = re.findall(r"\"page\":(\d+)",payload)[0]
            #         pageNext = int(pageNow)+1
            #         payloadNext = payload.replace('"page":'+str(pageNow),'"page":'+str(pageNext))

            #         rawJsonNext = json.loads(payloadNext,strict=False)
            #         rawJsonNext = json.dumps(rawJsonNext)

            #         if(payloadNext not in self.payload_history):
            #             self.payload_history.append(payloadNext)
            #             yield scrapy.Request('https://www.sigmaaldrich.com/api',callback=self.parseProducts,body=rawJsonNext,method='POST',headers=self.headers,meta={'mainCat':mainCat,'payLoad':payloadNext},dont_filter=True)
            #     except Exception as e:
            #         self.fileReport.write("next error - "+str(e)+"\n")
            #         self.fileReport.flush()

        except Exception as e:
            self.fileReport.write("products error - "+payload+"\n")
            self.fileReport.flush()


    def parseDetail(self,response):
        baseUrl = response.url
        print(baseUrl)
        # print(response.text)
        mainCat = response.meta['mainCat']
        prodUrl = response.meta['productUrl']
        rawJson = json.loads(response.text)
        detail = rawJson['data']['getProductDetail']

        page_group = ''
        try:
            temp = []
            for x in detail['productCategories']:
                temp.append('https://www.sigmaaldrich.com/'+self.locale+"/"+self.lang+x['url'])
            page_group = ','.join(temp)
        except:pass

        images = []
        try:
            temp = []
            for x in detail['images']:
                try:
                    temp.append('https://www.sigmaaldrich.com'+x['largeUrl'])
                except:
                    temp.append('https://www.sigmaaldrich.com'+x['mediumUrl'])
            images = temp
        except:pass
        images = str(images)
        descriptions = '<div>'
        try:
            for x in detail['descriptions']:
                descriptions+="<h3>"+x['label']+"</h3>"
                for y in x['values']:
                    descriptions+="<div><span>"+y+"</span></div>"
        except:pass
        descriptions += '</div>'
        descriptions = descriptions.replace("<div></div>","")

        productCodes = []
        try:
            for x in detail['aliases']:
                temp = {'codeType':x['label'],'codeValue':x['value']}
                productCodes.append(temp)
        except:pass
        try:
            temp = {'codeType':'CAS Number','codeValue':detail['casNumber']}
            if(temp['codeValue'] is not None):
                productCodes.append(temp)
        except:pass
        try:
            temp = {'codeType':'Molecular Weight','codeValue':detail['molecularWeight']}
            if(temp['codeValue'] is not None):
                productCodes.append(temp)
        except:pass
        try:
            temp = {'codeType':'Empirical Formula','codeValue':detail['empiricalFormula']}
            if(temp['codeValue'] is not None):
                productCodes.append(temp)
        except:pass
        try:
            temp = {'codeType':'Linear Formula','codeValue':detail['linearFormula']}
            if(temp['codeValue'] is not None):
                productCodes.append(temp)
        except:pass
        try:
            for x in detail['synonyms']:
                temp = {'codeType':'Synonyms','codeValue':x}
                productCodes.append(temp)
        except:pass

        attributes=[]
        try:
            for x in detail['attributes']:
                val = []
                for y in x['values']:
                    val.append(y)

                temp = {x['label']:''}
                temp[x['label']] = val
                attributes.append(temp)
        except Exception as e:pass

        breadcrumbs = []
        try:
            x = detail['productCategories'][0]['url']
            temp = x.split('/')
            for te in temp:
                if(te!="products" and te!=""):
                    y = te.split("-")
                    temp2 = []
                    for z in y:
                        temp2.append(z.capitalize())
                    breadcrumbs.append(' '.join(temp2))
        except:pass 

        document = ''
        try:
            x = "https://www.sigmaaldrich.com"+detail['specificationSheet']['url']
            document+=x
        except:pass

        name1 = detail['name']
        try:
            name1 = html.unescape(name1)
        except:pass
        name2 = detail['description']
        try:
            name2= html.unescape(name2)
        except:pass
        p = {
            #'mainCat':mainCat,
            'Product_Number':detail['productKey'],
            'SKU':'',
            'Product_Name':name1,
            'Product_Name2':name2,
            'Product_Description':html.unescape(descriptions),
            'Product_Codes':html.unescape(str(productCodes)),
            'Product_Attributes':html.unescape(str(attributes)),
            'Price':'',
            'Page_URL':prodUrl,
            'Page_Group':page_group,
            'Image_URLS':images,
            'Document_URLS':document,
            'Availability':'',
            'Breadcrumb':'>'.join(breadcrumbs),
        }
        
        payloadz = '{"operationName":"SdsCertificateSearch","variables":{"productNumber":"'+str(detail['erpProductKey'])+'","brand":"'+str(detail['brand']['erpKey'])+'"},"query":"query SdsCertificateSearch($productNumber: String!, $brand: String) {\n  getSdsCertificateSearch(input: {productNumber: $productNumber, brand: $brand}) {\n    locale\n    region\n    productNumber\n    sds {\n      languages {\n        primaryLanguage\n        altLanguages\n        __typename\n      }\n      brand\n      __typename\n    }\n    brands\n    __typename\n  }\n}\n"}'
        rawJsonz = json.loads(payloadz,strict=False)
        rawJsonz = json.dumps(rawJsonz)
        
        yield scrapy.Request('https://www.sigmaaldrich.com/api',callback=self.parseDocument,body=rawJsonz,method='POST',headers=self.headers_price,meta={'p':p,'productNumber':detail['erpProductKey'],'brand':detail['brand']['erpKey'],'catalogId':detail['catalogId']},dont_filter=True)

        
    def parseDocument(self,response):

        p = response.meta['p']
        productNumber = response.meta['productNumber']
        brand = response.meta['brand']
        catalogId = response.meta['catalogId']
        try:
            temp = []
            if(p['Document_URLS']!='' and p['Document_URLS'] is not None):
                temp.append(p['Document_URLS'])
            rawJson = json.loads(response.text)['data']['getSdsCertificateSearch']
            prodNum = rawJson['productNumber']

            lang = rawJson['sds'][0]['languages']['primaryLanguage']
            alts = rawJson['sds'][0]['languages']['altLanguages']
            for alt in alts:
                temp.append("https://www.sigmaaldrich.com/"+lang+"/"+alt.lower()+"/sds/"+brand.lower()+"/"+str(prodNum).lower())

            p['Document_URLS'] = str(temp)
        except:pass

        payloadz = '{"operationName":"PricingAndAvailability","variables":{"displaySDS":false,"productNumber":"'+str(productNumber)+'","brand":"'+str(brand)+'","quantity":1,"catalogType":"'+str(catalogId)+'","orgId":null},"query":"query PricingAndAvailability($productNumber: String!, $brand: String, $quantity: Int!, $catalogType: CatalogType, $checkForPb: Boolean, $orgId: String, $materialIds: [String!], $displaySDS: Boolean = false) {\n  getPricingForProduct(input: {productNumber: $productNumber, brand: $brand, quantity: $quantity, catalogType: $catalogType, checkForPb: $checkForPb, orgId: $orgId, materialIds: $materialIds}) {\n    ...ProductPricingDetail\n    __typename\n  }\n}\n\nfragment ProductPricingDetail on ProductPricing {\n  productNumber\n  country\n  materialPricing {\n    ...ValidMaterialPricingDetail\n    __typename\n  }\n  discontinuedPricingInfo {\n    ...DiscontinuedMaterialPricingDetail\n    __typename\n  }\n  dchainMessage\n  __typename\n}\n\nfragment ValidMaterialPricingDetail on ValidMaterialPricing {\n  brand\n  type\n  currency\n  dealerId\n  listPriceCurrency\n  listPrice\n  shipsToday\n  freeFreight\n  sdsLanguages\n  catalogType\n  materialDescription\n  materialNumber\n  netPrice\n  packageSize\n  price\n  product\n  quantity\n  isPBAvailable\n  vendorSKU\n  availabilities {\n    ...Availabilities\n    __typename\n  }\n  additionalInfo {\n    ...AdditionalInfo\n    __typename\n  }\n  promotionalMessage {\n    ...PromotionalMessage\n    __typename\n  }\n  ... @include(if: $displaySDS) {\n    sdsLanguages\n    __typename\n  }\n  __typename\n}\n\nfragment Availabilities on MaterialAvailability {\n  date\n  key\n  plantLoc\n  quantity\n  displayFromLink\n  displayInquireLink\n  messageType\n  contactInfo {\n    contactPhone\n    contactEmail\n    __typename\n  }\n  availabilityOverwriteMessage {\n    messageKey\n    messageValue\n    messageVariable1\n    messageVariable2\n    messageVariable3\n    __typename\n  }\n  supplementaryMessage {\n    messageKey\n    messageValue\n    messageVariable1\n    messageVariable2\n    messageVariable3\n    __typename\n  }\n  __typename\n}\n\nfragment AdditionalInfo on CartAdditionalInfo {\n  carrierRestriction\n  unNumber\n  tariff\n  casNumber\n  jfcCode\n  pdcCode\n  __typename\n}\n\nfragment PromotionalMessage on PromotionalMessage {\n  messageKey\n  messageValue\n  messageVariable1\n  messageVariable2\n  messageVariable3\n  __typename\n}\n\nfragment DiscontinuedMaterialPricingDetail on DiscontinuedMaterialPricing {\n  errorMsg\n  paramList\n  hideReplacementProductLink\n  displaySimilarProductLabel\n  hideTechnicalServiceLink\n  replacementProducts {\n    ...ReplacementProductDetail\n    __typename\n  }\n  alternateMaterials {\n    ...AlternateMaterialDetail\n    __typename\n  }\n  __typename\n}\n\nfragment ReplacementProductDetail on Product {\n  productNumber\n  name\n  description\n  sdsLanguages\n  images {\n    mediumUrl\n    altText\n    __typename\n  }\n  brand {\n    key\n    erpKey\n    name\n    logo {\n      smallUrl\n      altText\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment AlternateMaterialDetail on Material {\n  number\n  __typename\n}\n"}'
        rawJsonz = json.loads(payloadz,strict=False)
        rawJsonz = json.dumps(rawJsonz)

        yield scrapy.Request('https://www.sigmaaldrich.com/api',callback=self.parsePrice,body=rawJsonz,method='POST',headers=self.headers_price,meta={'p':p,'productNumber':productNumber,'brand':brand},dont_filter=True)

    def parsePrice(self,response):

        p = response.meta['p']
        compiledResult = []
        try:
            rawJson = json.loads(response.text)
            prices = rawJson['data']['getPricingForProduct']['materialPricing']
            for price in prices:
                q = p
                try:
                    q['SKU'] = price['materialNumber']
                    # tempPrice.append({'quantity':'1','unitSize':unitData,'sku':tdsku,'currency':'','price':''})
                    # q['Price'] = str(price['listPriceCurrency']) + " " + str(price['listPrice'])
                    q['Price'] = [{'quantity':'1','unitSize':price['packageSize'],'currency':str(price['listPriceCurrency']),'price':price['listPrice']}]
                    # print(q)
                    avail = ''
                    try:
                        avail += price['availabilities'][0]['key'].replace("_"," ")
                    except:pass
                    try:
                        avail += " " + datetime.strftime(datetime.fromtimestamp(price['availabilities'][0]['date']/1000),"%B %d,%Y")
                    except Exception as e:pass
                    try:
                        avail += " from " + price['availabilities'][0]['plantLoc'].replace("_"," ")
                    except:pass
                    
                    q['Availability'] = avail
                    # yield(q)
                    compiledResult.append({'price':q['Price']})
                    # print(compiledResult)
                    yield({'price':q['Price']})
                    
                except Exception as e:print(e)
        except:
            yield(p)

        return compiledResult