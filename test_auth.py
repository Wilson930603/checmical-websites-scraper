import pytest
import requests
import json
import time
from helper import AUTH_CREDENTIALS

production_server = 'http://13.40.107.142'
server = 'http://0.0.0.0'
price_url = f"{production_server}:8080/price"
page_url = f"{production_server}:8080/page"
bulk_url = f"{production_server}:8081/bulk"

# Test price
prices_json = [
    # {"Sitename":"sigmaaldrich","URL":"https://www.sigmaaldrich.com/US/en/product/mm/xx1014704","Username":"","Password":""},
    # {"Sitename":"vwr","URL":"https://us.vwr.com/store/product/4541052/vwr-microgrip-purple-nitrile-poly-coated-powder-freegloves","Username":"","Password":""},
    # {"Sitename":"faust","URL":"https://www.faust.ch/shop/Liquid_Handling/Microfluidics/Syringe_pumps/Accessories_for_Microlab_700$B$einfo185138_lang_UK.htm?UID=550062258554000000000000&OFS=0","Username":"","Password":""},
    # {"Sitename":"thermofisher","URL":"https://www.thermofisher.com/order/catalog/product/A29132?SID=srch-srp-A29132","Username":"","Password":""},
]
price_responses = {
    'sigmaaldrich': {
        "price": [
            [
                {
                    "currency": "$",
                    "price": "155.00",
                    "quantity": "1",
                    "unitSize": "1 EA"
                }
            ]
        ]
        },
    'vwr': [
        {
            "price": [
                {
                    "currency": "USD",
                    "price": "$65.90",
                    "quantity": "1",
                    "sku": "40101-440PK",
                    "unitSize": "Pack of 100"
                },
                {
                    "currency": "USD",
                    "price": "$547.62",
                    "quantity": "1",
                    "sku": "40101-440CS",
                    "unitSize": "Case of 1000"
                }
            ]
        },
        {
            "price": [
                {
                    "currency": "USD",
                    "price": "$65.90",
                    "quantity": "1",
                    "sku": "40101-344PK",
                    "unitSize": "Pack of 100"
                },
                {
                    "currency": "USD",
                    "price": "$547.62",
                    "quantity": "1",
                    "sku": "40101-344CS",
                    "unitSize": "Case of 1000"
                }
            ]
        },
        {
            "price": [
                {
                    "currency": "USD",
                    "price": "$65.90",
                    "quantity": "1",
                    "sku": "40101-346PK",
                    "unitSize": "Pack of 100"
                },
                {
                    "currency": "USD",
                    "price": "$547.62",
                    "quantity": "1",
                    "sku": "40101-346CS",
                    "unitSize": "Case of 1000"
                }
            ]
        },
        {
            "price": [
                {
                    "currency": "USD",
                    "price": "$65.90",
                    "quantity": "1",
                    "sku": "40101-348PK",
                    "unitSize": "Pack of 100"
                },
                {
                    "currency": "USD",
                    "price": "$547.62",
                    "quantity": "1",
                    "sku": "40101-348CS",
                    "unitSize": "Case of 1000"
                }
            ]
        },
        {
            "price": [
                {
                    "currency": "USD",
                    "price": "$65.90",
                    "quantity": "1",
                    "sku": "40101-350PK",
                    "unitSize": "Pack of 100"
                },
                {
                    "currency": "USD",
                    "price": "$547.62",
                    "quantity": "1",
                    "sku": "40101-350CS",
                    "unitSize": "Case of 1000"
                }
            ]
        }
    ],
    'faust': [
        {
            "price": [
                {
                    "currency": "CHF",
                    "price": "1'575.10",
                    "quantity": 1,
                    "unitSize": "1 PK"
                }
            ]
        },
        {
            "price": [
                {
                    "currency": "CHF",
                    "price": "728.80",
                    "quantity": 1,
                    "unitSize": "1 PK"
                }
            ]
        },
        {
            "price": [
                {
                    "currency": "CHF",
                    "price": "817.80",
                    "quantity": 1,
                    "unitSize": "1 PK"
                }
            ]
        },
        {
            "price": [
                {
                    "currency": "CHF",
                    "price": "614.70",
                    "quantity": 1,
                    "unitSize": "1 PK"
                }
            ]
        },
        {
            "price": [
                {
                    "currency": "CHF",
                    "price": "6.55",
                    "quantity": 1,
                    "unitSize": "1 PK"
                }
            ]
        }
    ],
    'thermofisher': [[
        {
            "currency": "GBP",
            "price": "Orderable",
            "quantity": 1,
            "unitSize": "6 x 1 mL"
        }
    ]],
}


# @pytest.mark.parametrize("body", prices_json)
# def test_price(body):
#     print('\n PRICE ================')

#     site = body['Sitename']
#     credential = AUTH_CREDENTIALS[site]
#     body['Username'] = credential['username']
#     body['Password'] = credential['password']
#     print(body)
#     response = requests.post(price_url, data=json.dumps(body))
#     print(response.text)
#     if site in price_responses:
#         assert json.loads(response.text) == price_responses[site]
#     assert response.status_code == 200
#     time.sleep(10)


# Test page
pages_json = [
    {"Sitename":"sigmaaldrich","URL":"https://www.sigmaaldrich.com/US/en/products/filtration/filter-paper","Username":"","Password":""},
    # {"Sitename":"vwr","URL":"https://us.vwr.com/store/category/adhesives/3617154","Username":"","Password":""},
    # {"Sitename":"faust","URL":"https://www.faust.ch/shop/Liquid_Handling/Microfluidics/Syringe_pumps/Accessories_for_Microlab_700$B$einfo185138_lang_UK.htm?UID=550062258554000000000000&OFS=0","Username":"","Password":""},
    # {"Sitename":"thermofisher","URL":"https://www.thermofisher.com/search/browse/category/us/en/90140059/pipette-tips","Username":"","Password":""},
]


@pytest.mark.parametrize("body", pages_json)
def test_page(body):
    print('\n PAGE ================')

    # Test auth
    credential = AUTH_CREDENTIALS[body['Sitename']]
    body['Username'] = credential['username']
    body['Password'] = credential['password']
    print(body)
    response = requests.post(page_url, data=json.dumps(body))
    print(response.text)
    assert response.status_code == 200
    # time.sleep(30)


# # Test bulk
bulks_json = [
    {"Sitename":"sigmaaldrich","Country":"CH","Language":"EN","Filename":"auth-sigma-1xxx.json","Username":"","Password":""},
    # {"Sitename":"vwr","Country":"US","Language":"EN","Filename":"auth-vwr-12xxx.json","Username":"","Password":""},
    # {"Sitename":"faust","Country":"CH","Language":"EN","Filename":"auth-faust-12xxx.json","Username":"","Password":""},
    {"Sitename":"thermofisher","Country":"","Language":"","Filename":"auth-thermofisher-12xxx.json","Username":"","Password":""},
]


# @pytest.mark.parametrize("body", bulks_json)
# def test_bulk(body):
#     print('\n BULK ================')

#     # Test auth
#     credential = AUTH_CREDENTIALS[body['Sitename']]
#     body['Username'] = credential['username']
#     body['Password'] = credential['password']
#     print(body)
#     response = requests.post(bulk_url, data=json.dumps(body))
#     assert response.status_code == 200
#     print(response.text)
