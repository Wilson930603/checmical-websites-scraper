## Sigmaaldrich, vwr, fishersci, faust, thermofisher scraping API 

### Usage & Syntax For Server
###### run flask in background / screen.
###### python3 flask-server1.py
###### python3 flask-server2.py
###### python3 uploader.py

### Usage & Syntax For Client (Use HTTP POST)
###http://13.40.107.142:8081/bulk
{"Sitename":"sigmaaldrich","Country":"CH","Language":"EN","Filename":"sigma-1xxx.json","Username":"","Password":""}
{"Sitename":"vwr","Country":"US","Language":"EN","Filename":"vwr-12xxx.json","Username":"","Password":""}
{"Sitename":"faust","Country":"CH","Language":"EN","Filename":"faust-12xxx.json","Username":"","Password":""}
{"Sitename":"fishersci","Country":"CH","Language":"EN","Filename":"fishersci-12xxx.json","Username":"","Password":""}
{"Sitename":"thermofisher","Country":"","Language":"","Filename":"thermofisher-12xxx.json","Username":"","Password":""}
 
###http://13.40.107.142:8080/page (can use product/category URL)
{"Sitename":"sigmaaldrich","URL":"https://www.sigmaaldrich.com/US/en/products/filtration/filter-paper","Username":"","Password":""}
{"Sitename":"vwr","URL":"https://us.vwr.com/store/category/adhesives/3617154","Username":"","Password":""}
{"Sitename":"faust","URL":"https://www.faust.ch/shop/Liquid_Handling/Microfluidics/Syringe_pumps/Accessories_for_Microlab_700$B$einfo185138_lang_UK.htm?UID=550062258554000000000000&OFS=0","Username":"","Password":""}
{"Sitename":"fishersci","URL":"https://www.fishersci.co.uk/gb/en/products/I9C8KVO5/antibody-production-purification.html","Username":"","Password":""}
{"Sitename":"thermofisher","URL":"https://www.thermofisher.com/search/browse/category/us/en/90140059/pipette-tips","Username":"","Password":""}
 
###http://13.40.107.142:8080/price
{"Sitename":"sigmaaldrich","URL":"https://www.sigmaaldrich.com/US/en/product/mm/xx1014704","Username":"","Password":""}
{"Sitename":"vwr","URL":"https://us.vwr.com/store/product/4541052/vwr-microgrip-purple-nitrile-poly-coated-powder-freegloves","Username":"","Password":""}
{"Sitename":"faust","URL":"https://www.faust.ch/shop/Liquid_Handling/Microfluidics/Syringe_pumps/Accessories_for_Microlab_700$B$einfo185138_lang_UK.htm?UID=550062258554000000000000&OFS=0","Username":"","Password":""}
{"Sitename":"fishersci","URL":"https://www.fishersci.co.uk/shop/products/bd-cytometric-bead-array-rat-tnf-flex-set-standard/15859428","Username":"","Password":""}
{"Sitename":"thermofisher","URL":"https://www.thermofisher.com/order/catalog/product/94300320?SID=srch-srp-94300320","Username":"","Password":""}

### Output
s3 buckets, json files.
