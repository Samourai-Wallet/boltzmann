'''
Created on 20200404
@author: TDevD (@SamouraiDev)
'''

import boltzmann.utils.segwit_addr

from btcpy.setup import setup
from btcpy.structs.crypto import PublicKey
from btcpy.structs.address import P2wpkhAddress, P2wshAddress
from btcpy.structs.script import ScriptPubKey

class Blockstream_Txo(object):
    '''
    A class storing a few data for a single txo (input or output)

    Attributes:
        n (int): The position of the TXO in the outputs of the transaction in
            which it was created.
        value (int): Value denominated in satoshis.
        address (str): Bitcoin address associated with the TXO.
        tx_idx (int): A special identifier assigned to each mined transaction
            by the Blockchain.info API. Set to `None` if not available. not
            currently read in this project.

        Note that coinbase transactions in the bitcoind-rpc interface and BCI API
        only contain the 'sequence' and 'script'/'coinbase' fields.
    '''

    def __init__(self, txo, mainnet):
        self.n = -1
        self.value = -1
        self.address = ''
        self.tx_idx = -1
        self.isMainNet = mainnet

        if self.isMainNet == True:
            setup('mainnet')
        else:
            setup('testnet')

        if txo is not None:

            if 'vout' in txo:
                self.n = txo['vout']

            if 'prevout' in txo:
                self.value = txo['prevout'].get('value')
            elif 'value' in txo:
                self.value = txo.get('value')

            # Gets the address or the scriptpubkey (if an address isn't associated to the txo)
            if 'prevout' in txo:
                self.address = txo['prevout'].get('scriptpubkey_address')
            elif 'scriptpubkey_address' in txo:
                self.address = txo.get('scriptpubkey_address')
            else:
                raise ValueError("Could not assign address to txo")

            self.tx_idx = None

    def __str__(self):
        return "{{ 'n': {0}, 'value':{1}, 'address':{2}, 'tx_idx':{3} }}".format(
            self.n, self.value, self.address, self.tx_idx)

    def __repr__(self):
        return self.__str__()


class Blockstream_Transaction(object):
    '''
    A class storing a few data for a single tx

    Attributes:
        height (int): 0-based height of block mining tx
        time (int): Unix timestamp for the time the transaction was received.
            Not currently used for analysis, and only provided by the
            Blockchain.info API and not bitcoind's RPC interface. If not
            available, set to `None`.
        txid (str): Lower-case hex representation of tx hash
        inputs (List[`transaction.Txo`])
        outputs (List[`transaction.Txo`])
    '''

    def __init__(self, _tx, _mainnet):

        tx = _tx
        height = tx.get('status').get('block_height')
        self.height = -1 if (height is None) else height
        self.time = tx.get('status').get('block_time')
        self.txid = tx['txid']
        self.inputs = []
        for txo_in in tx['vin']:
            txo_in['n'] = txo_in['vout']
            self.inputs.append(Blockstream_Txo(txo_in, _mainnet))
        self.outputs = []
        for txo_out in tx['vout']:
            txo_out['n'] = -1
            self.outputs.append(Blockstream_Txo(txo_out, _mainnet))

    def __str__(self):
        return "{{ 'height': {0}, 'time':{1}, 'txid':{2}, 'inputs':{3}, 'outputs':{4} }}".format(
            self.height, self.time, self.txid, self.inputs, self.outputs)

    def __repr__(self):
        return self.__str__()
