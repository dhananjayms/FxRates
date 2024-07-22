import boto3
from botocore.exceptions import ClientError
import http.client
import json
import os

TABLE_NAME = os.getenv("TABLE_NAME", default="FxRates")
API_URL = os.getenv("API_URL")

def get_FxRates():
    # Get FX Rates from www.alphavantage.co USD to JPY
    conn = http.client.HTTPSConnection("www.alphavantage.co")
    conn.request("GET", API_URL)
    response = conn.getresponse()

    if response.status == 200:
        data = json.loads(response.read().decode())
        json_data = data['Realtime Currency Exchange Rate']
        from_currency = json_data['1. From_Currency Code']
        to_currency = json_data['3. To_Currency Code']
        exchange_date = json_data['6. Last Refreshed']
        bid_price  = json_data['8. Bid Price']
        ask_price  = json_data['9. Ask Price']
        exchange_rate = json_data['5. Exchange Rate']

        # Return the FX Rates in the response
        return {"from_currency":from_currency, "to_currency":to_currency, "exchange_date" : exchange_date , "exchange_rate":exchange_rate , "bid_price": bid_price, "ask_price": ask_price }
    else:
        # Handle any errors
        return {"body": f"Failed to fetch FX Rates . Error code: {response.status}"}

def put_FxRates(fxRate):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)

    item = fxRate

    try:
        response = table.put_item(Item=item)
        return "FX Rate successfully written to FxRates."
    except ClientError as e:
        print(e)
        return "Error writing item to FxRates."
    
def lambda_handler(event, context):
    return put_FxRates(get_FxRates())
