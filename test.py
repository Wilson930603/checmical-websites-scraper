import pytest
import requests
import json

production_server = 'http://13.40.107.142'
server = 'http://0.0.0.0'
price_url = f"{server}:8080/price"
page_url = f"{server}:8080/page"
bulk_url = f"{server}:8081/bulk"

# Test price
prices_json = [
    {"Sitename":"sigmaaldrich","URL":"https://www.sigmaaldrich.com/US/en/product/mm/xx1014704","Username":"","Password":""},
    {"Sitename":"vwr","URL":"https://us.vwr.com/store/product/4541052/vwr-microgrip-purple-nitrile-poly-coated-powder-freegloves","Username":"","Password":""},
    {"Sitename":"faust","URL":"https://www.faust.ch/shop/Liquid_Handling/Microfluidics/Syringe_pumps/Accessories_for_Microlab_700$B$einfo185138_lang_UK.htm?UID=550062258554000000000000&OFS=0","Username":"","Password":""},
    {"Sitename":"fishersci","URL":"https://www.fishersci.co.uk/shop/products/bd-cytometric-bead-array-rat-tnf-flex-set-standard/15859428","Username":"","Password":""},
    {"Sitename":"thermofisher","URL":"https://www.thermofisher.com/order/catalog/product/A29132?SID=srch-srp-A29132","Username":"","Password":""},
]


@pytest.mark.parametrize("body", prices_json)
def test_price(body):
    print('\n================')
    print(body)

    # Test empty
    response = requests.post(price_url, data=json.dumps(body))
    print(response.text)
    assert response.status_code == 200


# Test page
pages_json = [
    {"Sitename":"sigmaaldrich","URL":"https://www.sigmaaldrich.com/US/en/products/filtration/filter-paper","Username":"","Password":""},
    {"Sitename":"vwr","URL":"https://us.vwr.com/store/category/adhesives/3617154","Username":"","Password":""},
    {"Sitename":"faust","URL":"https://www.faust.ch/shop/Liquid_Handling/Microfluidics/Syringe_pumps/Accessories_for_Microlab_700$B$einfo185138_lang_UK.htm?UID=550062258554000000000000&OFS=0","Username":"","Password":""},
    {"Sitename":"fishersci","URL":"https://www.fishersci.co.uk/gb/en/products/I9C8KVO5/antibody-production-purification.html","Username":"","Password":""},
    {"Sitename":"thermofisher","URL":"https://www.thermofisher.com/search/browse/category/us/en/90140059/pipette-tips","Username":"","Password":""},
]


@pytest.mark.parametrize("body", pages_json)
def test_page(body):
    print(body)

    # Test empty
    response = requests.post(page_url, data=json.dumps(body))
    print(response.text)
    assert response.status_code == 200


# Test bulk
bulks_json = [
    {"Sitename":"sigmaaldrich","Country":"CH","Language":"EN","Filename":"sigma-1xxx.json","Username":"","Password":""},
    {"Sitename":"vwr","Country":"US","Language":"EN","Filename":"vwr-12xxx.json","Username":"","Password":""},
    {"Sitename":"faust","Country":"CH","Language":"EN","Filename":"faust-12xxx.json","Username":"","Password":""},
    {"Sitename":"fishersci","Country":"CH","Language":"EN","Filename":"fishersci-12xxx.json","Username":"","Password":""},
    {"Sitename":"thermofisher","Country":"","Language":"","Filename":"thermofisher-12xxx.json","Username":"","Password":""},
]


@pytest.mark.parametrize("body", bulks_json)
def test_bulk(body):
    print(body)

    # Test empty
    response = requests.post(bulk_url, data=json.dumps(body))
    assert response.status_code == 200
    response = requests.post(page_url, data=json.dumps(body))
    print(response.text)
