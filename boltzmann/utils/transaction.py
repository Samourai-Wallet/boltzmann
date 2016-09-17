'''
Created on 20160917
Inspired from https://github.com/blockchain/api-v1-client-python by https://github.com/alecalve
@author: LaurentMT
'''


class Txo(object):
    '''
    A class storing a few data for a single txo (input or output)
    '''  
    def __init__(self, txo):
        if txo is not None:
            self.n = txo['n']
            self.value = txo['value']
            self.address = txo['addr']
            self.tx_idx = txo['tx_index']
            

class Transaction(object):
    '''
    A class storing a few data for a single tx
    '''  
    def __init__(self, tx):
        height = tx.get('block_height')
        self.height = -1 if (height is None) else height
        self.time = tx['time']
        self.txid = tx['hash']
        self.inputs = [Txo(txo_in.get('prev_out')) for txo_in in tx['inputs']]
        self.outputs = [Txo(txo_out) for txo_out in tx['out']]
        