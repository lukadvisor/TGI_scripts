# !pip install adal , If Required
import os
import adal
import requests
import json
import csv
from dotenv import load_dotenv
import datetime

sources = ['aldinord','aldisued','aldiuk',
            'amazon','amazonde','carrefour','discounto',
            'euroelectronics','homedepot','johnlewis',
            'leclerc','lidlde','lidles', 'lidlpl',
            'mediamarkt','metro','otto',
            'saturn','tchibode','walmart']

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
    print(f"Update statecode for {source} products...")
    #retailerquery = f"&$filter=contains(tk_RelatedProduct/tk_retailer,'{source}')"
    retailerquery = f"?$filter=contains(tk_retailer,'{source}')"

    # Request data.
    r = session.get(crmwebapi+crmwebapiquery_product+retailerquery)
    rawJson_str = r.content.decode('utf-8')
    rawJson = json.loads(rawJson_str)
    products = rawJson['value']

    for product in products:
        #product_id = product['_tk_relatedproduct_value']
        #statecode = product['tk_RelatedProduct']['statecode']
        #modifiedon = product['tk_RelatedProduct']['tk_lastcheckeddate']

        product_id = product['tk_customerproductmarketdataid']
        statecode = product['statecode']
        modifiedon = product['tk_lastcheckeddate']
        name = product['tk_name']

        first_date_str = modifiedon.split('T')[0]
        last_date = datetime.datetime.now()
        first_date = datetime.datetime.strptime(first_date_str, '%Y-%m-%d')
        difference = last_date - first_date
        difference_in_days = round(difference.total_seconds()/86400,1)

        if(statecode==0): #0=active, 1=inactive
            if(difference_in_days>=LIMIT):
                data = "{'value':1}"
                patch_query = f'({product_id})/statecode'
                r = session.put(crmwebapi+crmwebapiquery_product+patch_query, headers=headers, data=data)
                print(f"Product {product_id} not updated for {difference_in_days} days - Change statecode from 0 (active) to 1 (inactive)")
