from zeep import Client
from GD.settings.base import BASE_URL
ZARINPAL_CLIENT_URL = 'https://www.zarinpal.com/pg/services/WebGate/wsdl'
ZARINPAL_CALLBACKURL = BASE_URL + 'service/verify/'
ZARINPAL_PAYMENT_DESCRIPTION = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید" 
ZARINPAL_REDIRECT_WEBPAGE = '‫‪https://www.zarinpal.com/pg/StartPay/‬‬{}'
ZARINPAL_REDIRECT_MOBILEPAGE = '‫‪https://www.zarinpal.com/pg/StartPay/‬‬{}/MobileGate'
ZARINPAL_STATUS_OK = 100
ZARINPAL_STATUS_SUBMITTED = 101
zarin_client = Client(ZARINPAL_CLIENT_URL)
