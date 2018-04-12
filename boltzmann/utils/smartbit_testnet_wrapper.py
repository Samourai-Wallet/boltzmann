'''
Created on 20180411
@author: TDevD (@SamouraiDev)
'''
import json
from urllib.request import urlopen
from urllib.error import HTTPError
from boltzmann.utils.smartbit_transaction import Smartbit_Transaction
from boltzmann.utils.smartbit_data_wrapper import SmartbitDataWrapper


class SmartbitTestNetWrapper(SmartbitDataWrapper):
    '''
    A wrapper for smartbits api
    '''


    '''
    CONSTANTS
    '''
    # API base uri
    BASE_URI = "https://testnet-api.smartbit.com.au/"

    # Timeout
    TIMEOUT = 10


    def get_tx(self, txid):
        response = ''

        try:
            uri = self.BASE_URI + 'v1/blockchain/tx/' + txid
            response = urlopen(uri, None, timeout=self.TIMEOUT).read().decode('utf-8')
        except HTTPError as e:
            raise Exception(e.read(), e.code)

        json_response = json.loads(response)
        return Smartbit_Transaction(json_response)
