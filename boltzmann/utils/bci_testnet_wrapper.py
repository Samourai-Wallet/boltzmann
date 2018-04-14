'''
Created on 20180412
@author: TDevD (@SamouraiDev)
'''
import json
from urllib.request import urlopen
from urllib.error import HTTPError
from boltzmann.utils.transaction import Transaction
from boltzmann.utils.blockchain_data_wrapper import BlockchainDataWrapper


class BlockchainTestNetInfoWrapper(BlockchainDataWrapper):
    '''
    A wrapper for blockchain.info testnet api
    '''


    '''
    CONSTANTS
    '''
    # API base uri
    BASE_URI = "https://testnet.blockchain.info/"

    # Timeout
    TIMEOUT = 10


    def get_tx(self, txid):
        response = ''

        try:
            uri = self.BASE_URI + 'rawtx/' + txid
            response = urlopen(uri, None, timeout=self.TIMEOUT).read().decode('utf-8')
        except HTTPError as e:
            raise Exception(e.read(), e.code)

        json_response = json.loads(response)
        return Transaction(json_response)
