from urllib import response
from wsgiref import headers
from django.test import TestCase
from django.conf import settings
import requests
import json
# Create your tests here
def paystack_api(send): 
    url =  "https://api.paystack.co/transferrecipient"
    header = {"Authorization": f"Bear ['sk_test_dc7fc2fd68cae43e98647cd1e9fbe0f1ef105a60']"}
    r = requests.get(url, headers=header)
    response = r.json()
    print(response)
paystack_api('emmy')