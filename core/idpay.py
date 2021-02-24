import requests
from GD.settings.base import X_SANDBOX, X_API_KEY
import  json
# Payment not made
IDPAY_STATUS_1=1
# Payment failed
IDPAY_STATUS_2=2
# error ?
IDPAY_STATUS_3=3
# blocked
IDPAY_STATUS_4=4
# Return to payer
IDPAY_STATUS_5=5
# System reversal
IDPAY_STATUS_6=6
# Cancel payment
IDPAY_STATUS_7=7

# Awaiting payment confirmation
IDPAY_STATUS_10=10

# Payment is approved
IDPAY_STATUS_100=100
IDPAY_STATUS_101=101
# Was deposited
IDPAY_STATUS_200=200

# payment created
IDPAY_STATUS_201=201

IDPAY_PAYMENT_DESCRIPTION='register workshops or talks'
IDPAY_CALL_BACK='https://gamecraft.ce.aut.ac.ir/api/service/verify/'

IDPAY_URL="https://api.idpay.ir/v1.1/payment"
IDPAY_URL_VERIFY="https://api.idpay.ir/v1.1/payment/verify"

class IdPayRequest:
    def __init__(self):
        self.__headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': X_API_KEY,
            'X-SANDBOX': X_SANDBOX
        }

    def create_payment(self, order_id, amount, name, phone, mail, desc, callback):
        body = {
            "order_id": order_id,
            "amount": amount,
            "name": name,
            "phone": phone,
            "mail": mail,
            "desc": desc,
            "callback": callback
        }
        response=requests.request(method='POST',headers=self.__headers,url=IDPAY_URL,data=json.dumps(body))
        json_response=json.loads(response.text)
        json_response['status']=response.status_code
        # print(json_response)
        return json_response
    def verify_payment(self,order_id,payment_id):
        body = {
            "order_id": order_id,
            "id": payment_id,

        }
        response = requests.request(method='POST', headers=self.__headers, url=IDPAY_URL_VERIFY, data=json.dumps(body))
        json_response = json.loads(response.text)
        if 'status' not in json_response:
            json_response['status']=response.status_code
        print(json_response)
        return json_response

if __name__ == '__main__':
    IdPayRequest().verify_payment('101','96ad2b26317356cd9b56b76a64df3c3a')
