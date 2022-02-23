# !pip install adal , If Required
import os
import adal
import requests
import json
import csv
from dotenv import load_dotenv
import datetime

sources = ['lidles']

# Global configs.
load_dotenv(dotenv_path='.env')
CLIENT_ID = os.environ.get('CLIENT_ID')
RESOURCE_URI = os.environ.get('RESOURCE_URI')
AUTHORITY_URI = os.environ.get('AUTHORITY_URI')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

#After how many days to change statecode?
LIMIT = 30

# Get an access token.
context = adal.AuthenticationContext(AUTHORITY_URI, api_version=None)
token = context.acquire_token_with_client_credentials(RESOURCE_URI, CLIENT_ID, CLIENT_SECRET)
#print(token)

session = requests.Session()
session.headers.update(dict(Authorization='Bearer {}'.format(token.get('accessToken'))))
 
headers = {
    'Authorization': 'Bearer ' + token.get('accessToken'),
    'OData-MaxVersion': '4.0',
    'OData-Version': '4.0',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

#set these values to query your crm data

crmwebapi = RESOURCE_URI+'/api/data/v9.2/' #full path to web api endpoint
crmwebapiquery_product = 'tk_customerproductmarketdatas'#?$select=tk_name #web api query (include leading /)
crmwebapiquery_price = 'tk_customerproductmarketprices'#?$select=tk_features' #web api query (include leading /)
crmwebapiquery = 'tk_customerproductmarketprices?$expand=tk_RelatedProduct'

for source in sources:
    with open(f'{source}.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            recordid = str(row['Retailer']+'_'+row['Article no.'])

            rating = None
            number_of_reviews = None
            try:
                rating = round(float(row['Rating']),2)
                number_of_reviews = int(row['Number of reviews'])
            except:
                pass

            feb21 = datetime.datetime.strptime('2022-02-21','%Y-%m-%d')

            #add ratings to products
            filterquery = f"?$filter=tk_recordid eq '{recordid}'" 
            r = session.get(crmwebapi+crmwebapiquery_product+filterquery)
            rawJson_str = r.content.decode('utf-8')
            rawJson = json.loads(rawJson_str)
            products = rawJson['value']
            if not len(products):
                print("no product with this id")
                continue
            if(len(products)>1):
                print("problem: more than 1 product?")
                continue
            product = products[0]
            tk_lastcheckeddate = product['tk_lastcheckeddate']
            first_date_str = tk_lastcheckeddate.split('T')[0]
            first_date = datetime.datetime.strptime(first_date_str, '%Y-%m-%d')
            if first_date<feb21:
                continue
            name = product['tk_name']
            product_id = product['tk_customerproductmarketdataid']

            data = "{'value':"+str(rating)+"}"
            patch_query = f'({product_id})/tk_latestrating'
            r = session.put(crmwebapi+crmwebapiquery_product+patch_query, headers=headers, data=data)
            print(f"Product {name} - add rating to product record")

            data = "{'value':"+str(number_of_reviews)+"}"
            patch_query = f'({product_id})/tk_latestnumberofreview'
            r = session.put(crmwebapi+crmwebapiquery_product+patch_query, headers=headers, data=data)
            print(f"Product {name} - add reviews to product record")


            #price table
            filterquery = f"&$filter=tk_RelatedProduct/tk_recordid eq '{recordid}'" 
            sortquery = "&$orderby=modifiedon desc"
            r = session.get(crmwebapi+crmwebapiquery+filterquery+sortquery)
            rawJson = json.loads(r.content.decode('utf-8'))
            prices = rawJson['value']

            for price in prices:
                createdon = price['createdon']
                first_date_str = createdon.split('T')[0]
                first_date = datetime.datetime.strptime(first_date_str, '%Y-%m-%d')
                price_id = price['tk_customerproductmarketpriceid']
                if first_date<feb21:
                    continue

                data = "{'value':"+str(rating)+"}"
                patch_query = f'({price_id})/tk_rating'
                r = session.put(crmwebapi+crmwebapiquery_price+patch_query, headers=headers, data=data)
                print(f"Product {name} - add rating to price record")

                data = "{'value':"+str(number_of_reviews)+"}"
                patch_query = f'({price_id})/tk_numberofreviews'
                r = session.put(crmwebapi+crmwebapiquery_price+patch_query, headers=headers, data=data)
                print(f"Product {name} - add reviews to price record")
                