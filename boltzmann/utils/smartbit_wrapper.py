'''
Created on 20180416
@author: TDevD (@SamouraiDev)
'''
import json
from urllib.request import urlopen
from urllib.error import HTTPError
from boltzmann.utils.smartbit_transaction import Smartbit_Transaction
from boltzmann.utils.smartbit_data_wrapper import SmartbitDataWrapper


class SmartbitWrapper(SmartbitDataWrapper):
    '''
    A wrapper for smartbits api
    '''


    '''
    CONSTANTS
    '''
    # Timeout
    TIMEOUT = 10


    def get_tx(self, txid, mainnet):
        response = ''

        if mainnet == True:
            BASE_URI = "https://api.smartbit.com.au/"
        else:
            BASE_URI = "https://testnet-api.smartbit.com.au/"

        try:
            uri = BASE_URI + 'v1/blockchain/tx/' + txid
            response = urlopen(uri, None, timeout=self.TIMEOUT).read().decode('utf-8')
        except HTTPError as e:
            raise Exception(e.read(), e.code)

        json_response = json.loads(response)
        return Smartbit_Transaction(json_response, mainnet)
