import requests
from GD.settings.base import PAYPING_AUTH
import  json

PayPing_PAYMENT_DESCRIPTION='register workshops or talks'
PayPing_CALL_BACK='https://gamecraft.ce.aut.ac.ir/api/v2/service/verify/'

PayPing_URL="https://api.payping.ir/v2/pay"
PayPing_URL_VERIFY="https://api.payping.ir/v2/pay/verify"
def PayPingPeymentLinkGenerator(code):
    return f'https://api.payping.ir/v2/pay/gotoipg/{code}'
class PayPingRequest:
    def __init__(self):
        self.__headers = {
            'Content-Type': 'application/json',
            "Authorization": "Bearer " + PAYPING_AUTH
        }

    def create_payment(self, order_id, amount, name, phone, mail, desc, callback):
        body = {
            "amount": amount,
            "payerIdentity": email,
            "payerName": name,
            "description": desc,
            "returnUrl": callback,
            "clientRefId": order_id
           }
        response=requests.request(method='POST',headers=self.__headers,url=PayPing_URL,data=json.dumps(body))
        json_response=json.loads(response.text)
        json_response['status']=response.status_code
        # print(json_response)
        return json_response
        
    def verify_payment(self,amount ,payment_id):
        body = {
            "refId": payment_id,
            "amount": amount
        }
        response = requests.request(method='POST', headers=self.__headers, url=PayPing_URL_VERIFY, data=json.dumps(body))
        json_response = json.loads(response.text)
        if 'status' not in json_response:
            json_response['status']=response.status_code
        print(json_response)
        return json_response

if __name__ == '__main__':
    PayPingRequest().verify_payment('101','96ad2b26317356cd9b56b76a64df3c3a')
