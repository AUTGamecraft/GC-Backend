import requests
from GD.settings.base import PAYPING_AUTH
import  json

PAYPING_ERRORCODES = {
    
}

PAYPING_STATUS_OK = 200
PAYPING_STATUS_201 = 201
PAYPING_STATUS_202 = 202
PAYPING_STATUS_CLIENT_ERROR = 400
PAYPING_STATUS_SERVER_ERROR = 500
PAYPING_STATUS_503 = 503
PAYPING_STATUS_AUTH_ERROR = 401
PAYPING_STATUS_403 = 403
PAYPING_STATUS_404 = 404
PAYPING_STATUS_500 = 500






PayPing_PAYMENT_DESCRIPTION='register workshops or talks'
PayPing_CALL_BACK='https://gamecraft.ce.aut.ac.ir/api/v2/service/verify'

PayPing_URL="https://zify.ir/api/order/v2/create"
PayPing_URL_VERIFY="https://zify.ir/api/order/v2/verify"
def PayPingPeymentLinkGenerator(code):
    return f'https://zify.ir/order/accept/{code}'
class PayPingRequest:
    def __init__(self):
        self.__headers = {
            'Content-Type': 'application/json',
            "Authorization": "Bearer " + PAYPING_AUTH
        }

    def create_payment(self, order_id, amount, name, phone, mail, desc, callback):
        body = {
            "payer" : {
                "first_name": "",
                "last_name": name,
                "phone": phone,
                "email": mail,
                "state": "",
                "city": "",
                "address_1": "",
                "address_2": "",

            },
            "products" :[
                {
                "code": "000",
                "sellQuantity": 1,
                "title": "GAME CRAFT PAY",
                "amount": amount,
                "unlimited": True,
                "quantity": 100,
                "description": PayPing_PAYMENT_DESCRIPTION
                }
            ],
            "returnUrl": PayPing_CALL_BACK,
            "clientRefId": order_id,
            "shipping_total": 0,
            "off_total": 0,
            "tax_total": 0
           }
        response=requests.request(method='POST',headers=self.__headers,url=PayPing_URL,data=json.dumps(body))
        json_response=json.loads(response.text)
        json_response['status']=response.status_code
        return json_response
        
    def verify_payment(self, code):
        body = {
            "order": code
        }
        response = requests.request(method='POST', headers=self.__headers, url=PayPing_URL_VERIFY, data=json.dumps(body))
        json_response = json.loads(response.text)
        if 'status' not in json_response:
            json_response['status']=response.status_code
        print(json_response)
        return json_response

if __name__ == '__main__':
    PayPingRequest().verify_payment('101','96ad2b26317356cd9b56b76a64df3c3a')
