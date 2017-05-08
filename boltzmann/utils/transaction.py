'''
Created on 20160917
Inspired from https://github.com/blockchain/api-v1-client-python by https://github.com/alecalve
@author: LaurentMT
'''


class Txo(object):
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
    def __init__(self, txo):
        self.n = -1
        self.value = -1
        self.address = ''
        self.tx_idx = -1

        if txo is not None:
            if 'n in txo':
                self.n = txo['n']
            if 'value' in txo:
                self.value = txo['value']
            # Gets the address or the scriptpubkey (if an address isn't associated to the txo)
            if 'addr' in txo:
                self.address = txo['addr'] 
            elif 'script' in txo:
                self.address = txo['script']
            else:
                raise ValueError("Could not assign address to txo")

            self.tx_idx = txo['tx_index']

    def __str__(self):
        return "{{ 'n': {0}, 'value':{1}, 'address':{2}, 'tx_idx':{3} }}".format(
            self.n, self.value, self.address, self.tx_idx)

    def __repr__(self):
        return self.__str__()


class Transaction(object):
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
    def __init__(self, tx):
        height = tx.get('block_height')
        self.height = -1 if (height is None) else height
        self.time = tx['time']
        self.txid = tx['hash']
        self.inputs = [Txo(txo_in.get('prev_out')) for txo_in in tx['inputs']]
        self.outputs = [Txo(txo_out) for txo_out in tx['out']]

    def __str__(self):
        return "{{ 'height': {0}, 'time':{1}, 'txid':{2}, 'inputs':{3}, 'outputs':{4} }}".format(
            self.height, self.time, self.txid, self.inputs, self.outputs)

    def __repr__(self):
        return self.__str__()
