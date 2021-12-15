# !pip install adal , If Required
import adal
import requests
import json
import csv
import sys
import os.path
import os
from dotenv import load_dotenv

# Global configs.
load_dotenv(dotenv_path='.env')
CLIENT_ID = os.environ.get('CLIENT_ID')
RESOURCE_URI = os.environ.get('RESOURCE_URI')
AUTHORITY_URI = os.environ.get('AUTHORITY_URI')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

#set these values to query your crm data

crmwebapi = 'https://mysam-config.api.crm5.dynamics.com/api/data/v9.2/' #full path to web api endpoint
crmwebapiquery_product = 'tk_customerproductmarketdatas'#?$select=tk_features' #web api query (include leading /)
crmwebapiquery_price = 'tk_customerproductmarketprices'#?$select=tk_features' #web api query (include leading /)
crmwebapiquery = 'tk_customerproductmarketprices?$expand=tk_RelatedProduct'


def main():

    source = sys.argv[1]
    file_exist = os.path.isfile(f"{source}.csv")
    if not file_exist:
        print(f"ERROR! file {source}.csv does not exist")
        return(0)

    # Get an access token.
    context = adal.AuthenticationContext(AUTHORITY_URI, api_version=None)
    token = context.acquire_token_with_client_credentials(RESOURCE_URI, CLIENT_ID, CLIENT_SECRET)

    session = requests.Session()
    session.headers.update(dict(Authorization='Bearer {}'.format(token.get('accessToken'))))
     
    # Request data.
    r = session.get(crmwebapi+crmwebapiquery_product)
    rawJson = r.content.decode('utf-8')
    #print(rawJson)

    #if we have an accesstoken
    if(token):
        #prepare the crm request headers
        headers_post = {
            'Authorization': 'Bearer ' + token.get('accessToken'),
            'OData-MaxVersion': '4.0',
            'OData-Version': '4.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=utf-8',
            'Prefer': 'return=representation'
        }

        headers_patch = {
            'Authorization': 'Bearer ' + token.get('accessToken'),
            'OData-MaxVersion': '4.0',
            'OData-Version': '4.0',
            'Accept': 'application/json',
            'If-Match': '*',
            'Content-Type': 'application/json; charset=utf-8',
            'Prefer': 'return=representation'
        }

        with open(f'{source}.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:

                recordid = str(row['Retailer']+'_'+row['Article no.'])

                #get most recent record with this recordid
                filterquery = f"&$filter=contains(tk_RelatedProduct/tk_recordid,'{recordid}')" 
                sortquery = "&$orderby=modifiedon desc"
                r = session.get(crmwebapi+crmwebapiquery+filterquery+sortquery)
                rawJson = json.loads(r.content.decode('utf-8'))
                products = rawJson['value']
                product_id = None
                previous_price = None
                if(len(products)): #number 0 is most recent
                    product_id = products[0]['_tk_relatedproduct_value']
                    price_id = products[0]['tk_customerproductmarketpriceid']
                    previous_price = products[0]['tk_retailprice']

                data_product = {
                        'tk_productcategory': row['Product category (english)'],
                        'tk_brandname': row['Brand name'],
                        'tk_retailer': row['Retailer'],
                        'tk_articleno': row['Article no.'],
                        'tk_name': row['Article description'],
                        'tk_articledescription': row['Features'],
                        'tk_articledescriptionenglish': row['Features (english)'],
                        'tk_producturl': row['Product link'],
                        'tk_pictureurl': row['Picture url'],
                        'tk_recordid': recordid,
                    }

                data_str = json.dumps(data_product)

                if not product_id:
                    r = session.post(crmwebapi+crmwebapiquery_product, headers=headers_post, data=data_str)
                    print(f"Adding new item with id: {recordid}:")
                else:
                    patch_query = f'({product_id})'
                    r = session.patch(crmwebapi+crmwebapiquery_product+patch_query, headers=headers_patch, data=data_str)
                    print(f"Updating item with id {recordid}:")

                rawJson = r.content.decode('utf-8')
                #print(rawJson)

                if(r.status_code==200 or r.status_code==201 or r.status_code==204):
                    product_id = json.loads(rawJson)["tk_customerproductmarketdataid"]
                    name = json.loads(rawJson)["tk_name"]

                    rating = None
                    number_of_reviews = None
                    try:
                        rating = round(float(row['Rating']),2)
                        number_of_reviews = int(row['Number of reviews'])
                    except:
                        pass

                    price = None
                    try:
                        price = float(row['Retail price'])
                    except:
                        pass

                    print(row['Currency'])
                    data_price = {
                        'tk_retailprice': price,
                        'tk_rating': rating,
                        'tk_numberofreviews': number_of_reviews,
                        'transactioncurrencyid': row['Currency'], #need to be fixed
                        'tk_RelatedProduct@odata.bind': f'/tk_customerproductmarketdatas({product_id})'
                    }

                    data_str = json.dumps(data_price)
                    r = session.post(crmwebapi+crmwebapiquery_price, headers=headers_post, data=data_str)
                    rawJson = r.content.decode('utf-8')
                    print(rawJson)
                    price = json.loads(rawJson)["tk_retailprice"]
                    print(f"..{name} with price: {price}")

                else:
                    print(rawJson)


if __name__ == "__main__":
    main()
