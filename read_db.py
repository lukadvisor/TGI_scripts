# !pip install adal , If Required
import adal
import requests
import json
import csv

# Global configs.
CLIENT_ID = '143d00f8-4e4e-4538-b656-ff5410e9c50b'
RESOURCE_URI = 'https://mysam-config.crm5.dynamics.com'
AUTHORITY_URI = 'https://login.microsoftonline.com/12457c39-cb83-48e2-8265-0ad72e99c09d'
CLIENT_SECRET = 'TZa7Q~6fHq.DyQQ9gn5AvModq389KI3qa0AdC'

#BE VERY CAREFUL!! SETTING THIS TO TRUE WILL DELETE ENTIRE DATABASE!!!
delete = False #ONLY FOR DEBUG PURPOSE! BE CAREFUL!!

# Get an access token.
context = adal.AuthenticationContext(AUTHORITY_URI, api_version=None)
token = context.acquire_token_with_client_credentials(RESOURCE_URI, CLIENT_ID, CLIENT_SECRET)
#print(token)

session = requests.Session()
session.headers.update(dict(Authorization='Bearer {}'.format(token.get('accessToken'))))
 
#set these values to query your crm data

crmwebapi = 'https://mysam-config.api.crm5.dynamics.com/api/data/v9.2/' #full path to web api endpoint
crmwebapiquery_product = 'tk_customerproductmarketdatas'#?$select=tk_name #web api query (include leading /)
crmwebapiquery_price = 'tk_customerproductmarketprices'#?$select=tk_features' #web api query (include leading /)
crmwebapiquery = 'tk_customerproductmarketprices?$expand=tk_RelatedProduct'
filterquery = "&$filter=contains(tk_RelatedProduct/tk_recordid,'discounto_3121040071731')" 
sortquery = "&$orderby=modifiedon desc"
retailerquery = "&$filter=contains(tk_RelatedProduct/tk_retailer,'discounto')"
#filterapi_productonly = "&$filter=contains(tk_recordid,'discounto_3121040071731')"

# Request data.
r = session.get(crmwebapi+crmwebapiquery)
#r = session.get(crmwebapi+crmwebapiquery+filterquery+sortquery)
rawJson_str = r.content.decode('utf-8')
#print(rawJson_str)
rawJson = json.loads(rawJson_str)
products = rawJson['value']

for product in products[0:100]:
    if not delete:
        print(product)

    if(delete):
        price_id = product['tk_customerproductmarketpriceid']
        product_id = product['_tk_relatedproduct_value']
        
        headers = {
            'Authorization': 'Bearer ' + token.get('accessToken'),
            'OData-MaxVersion': '4.0',
            'OData-Version': '4.0',
            'Content-Type': 'application/json'
        }

        print(f"Deleting item {product_id}")
        r = session.delete(crmwebapi+crmwebapiquery_product+f'({product_id})', headers=headers)
        print(r.status_code)
        print(f"Deleting price {price_id}")
        r = session.delete(crmwebapi+crmwebapiquery_price+f'({price_id})', headers=headers)
        print(r.status_code)


