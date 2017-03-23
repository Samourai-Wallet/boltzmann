'''
Created on 20160917
Inspired from https://github.com/blockchain/api-v1-client-python by https://github.com/alecalve
@author: LaurentMT
'''
import json
from urllib.request import urlopen
from urllib.error import HTTPError
from boltzmann.utils.transaction import Transaction
from boltzmann.utils.blockchain_data_wrapper import BlockchainDataWrapper


class BlockchainInfoWrapper(BlockchainDataWrapper):
    '''
    A wrapper for blockchain.info api
    '''


    '''
    CONSTANTS
    '''
    # API base uri
    BASE_URI = "https://blockchain.info/"

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
