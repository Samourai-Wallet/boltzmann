'''
Created on 20160917
Inspired from https://github.com/blockchain/api-v1-client-python by https://github.com/alecalve
@author: LaurentMT
'''

from btcpy.setup import setup
from btcpy.structs.crypto import PublicKey
from btcpy.structs.address import P2wpkhAddress

import boltzmann.utils.segwit_addr

class Smartbit_Txo(object):
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
            elif 'n' in txo:
                self.n = txo['n']
            if 'value_int' in txo:
                self.value = txo['value_int']
            # Gets the address or the scriptpubkey (if an address isn't associated to the txo)
            if 'addresses' in txo:
                addresses = txo['addresses']
                if len(addresses) > 0:
                    self.address = addresses[0]
                elif 'type' in txo:
                    if txo['type'] == 'witness_v0_keyhash':
                        if 'script_pub_key' in txo:
                            script_pub_key = txo['script_pub_key']
                            hex = script_pub_key['hex']
                            if self.isMainNet == True:
                                self.address = boltzmann.utils.segwit_addr.encode('bc', 0, bytes.fromhex(hex[4:]))
                            else:
                                self.address = boltzmann.utils.segwit_addr.encode('tb', 0, bytes.fromhex(hex[4:]))
                        elif 'witness' in txo:
                            witness = txo['witness']
                            if len(witness) >= 1:
                                pubkey_hex = witness[1];
                                pubkey = PublicKey.unhexlify(pubkey_hex)
                                segwit_address = P2wpkhAddress(pubkey.hash(), version=0)
                                self.address = str(segwit_address)
                            else:
                                self.address = txo['type']
                        else:
                            self.address = txo['type']
            elif 'script_sig' in txo:
                script_sig = txo['script_sig']
                self.address = script_sig['hex']
            elif 'script_pub_key' in txo:
                script_pub_key = txo['script_pub_key']
                self.address = script_pub_key['hex']
            else:
                raise ValueError("Could not assign address to txo")

            self.tx_idx = None

    def __str__(self):
        return "{{ 'n': {0}, 'value':{1}, 'address':{2}, 'tx_idx':{3} }}".format(
            self.n, self.value, self.address, self.tx_idx)

    def __repr__(self):
        return self.__str__()


class Smartbit_Transaction(object):
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

        tx = _tx.get('transaction')
        height = tx.get('block')
        self.height = -1 if (height is None) else height
        self.time = tx['time']
        self.txid = tx['txid']
        self.inputs = [Smartbit_Txo(txo_in, _mainnet) for txo_in in tx['inputs']]
        self.outputs = [Smartbit_Txo(txo_out, _mainnet) for txo_out in tx['outputs']]

    def __str__(self):
        return "{{ 'height': {0}, 'time':{1}, 'txid':{2}, 'inputs':{3}, 'outputs':{4} }}".format(
            self.height, self.time, self.txid, self.inputs, self.outputs)

    def __repr__(self):
        return self.__str__()
