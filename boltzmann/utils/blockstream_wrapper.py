'''
Created on 20200404
@author: TDevD (@SamouraiDev)
'''
import json
import gzip

from urllib.request import urlopen
from urllib.error import HTTPError
from boltzmann.utils.blockstream_transaction import Blockstream_Transaction
from boltzmann.utils.blockstream_data_wrapper import BlockstreamDataWrapper

class BlockstreamWrapper(BlockstreamDataWrapper):
    '''
    A wrapper for blockstream api
    '''


    '''
    CONSTANTS
    '''
    # Timeout
    TIMEOUT = 10


    def get_tx(self, txid, mainnet):
        response = ''

        if mainnet == True:
            BASE_URI = "https://blockstream.info/api/"
        else:
            BASE_URI = "https://blockstream.info/testnet/api/"

        try:
            uri = BASE_URI + 'tx/' + txid
            response = urlopen(uri, None, timeout=self.TIMEOUT).read()
            # check for gzip response
            if response[0] == 0x1f and response[1] == 0x8b:
                response = gzip.decompress(response)
        except HTTPError as e:
            raise Exception(e.read(), e.code)

        json_response = json.loads(response)
        return Blockstream_Transaction(json_response, mainnet)
