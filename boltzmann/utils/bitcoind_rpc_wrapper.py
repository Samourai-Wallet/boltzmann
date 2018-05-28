'''
Fetch the bare minimum data from bitcoind RPC required to be compatible.
Created on 20170124
@author: kristovatlas
'''
import os
import decimal
from warnings import warn
from bitcoinrpc.authproxy import AuthServiceProxy
from boltzmann.utils.transaction import Transaction
from boltzmann.utils.blockchain_data_wrapper import BlockchainDataWrapper

class MissingRPCConfigurationError(Exception):
    """Configuration for RPC connection is missing."""
    def __init__(self, msg):
        self.msg = msg
        super(MissingRPCConfigurationError, self).__init__()

    def __str__(self):
        return "MissingRPCConfigurationError with {0}".format(self.msg)


class NoDataAvailableForGenesisBlockError(Exception):
    """No data available for the genesis block from bitcoind.

    If the requested tx is the sole transaction of the genesis block, bitcoind's
    RPC interface will throw an error 'No information available about
    transaction (code -5)'
    """
    pass


class PrevOutAddressCannotBeDecodedError(Exception):
    """Raised when a previous transaction's output address can't be decoded by RPC."""
    def __init__(self, msg):
        self.msg = msg
        super(PrevOutAddressCannotBeDecodedError, self).__init__()

    def __str__(self):
        return "PrevOutAddressCannotBeDecodedError with {0}".format(self.msg)


class BitcoindRPCWrapper(BlockchainDataWrapper):
    '''
    A connection manager for bitcoind's RPC interface

    All RPC configuration variables will be set using the following env vars:
        * BOLTZMANN_RPC_USERNAME
        * BOLTZMANN_RPC_PASSWORD
        * BOLTZMANN_RPC_HOST
        * BOLTZMANN_RPC_PORT
    '''

    GENESIS_BLOCK = { #rpc-style format
        'txid':    ('4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2'
                    '127b7afdeda33b'),
        'version':  1,
        'locktime': 0,
        'vin': [{
            "sequence":4294967295,
            'coinbase': ('04ffff001d0104455468652054696d65732030332f4a6'
                         '16e2f32303039204368616e63656c6c6f72206f6e2062'
                         '72696e6b206f66207365636f6e64206261696c6f75742'
                         '0666f722062616e6b73')
        }],
        'vout': [
            {
                'value': 50.00000000,
                'n': 0,
                'scriptPubKey': {
                    'asm': ('04678afdb0fe5548271967f1a67130b7105cd6a828'
                            'e03909a67962e0ea1f61deb649f6bc3f4cef38c4f3'
                            '5504e51ec112de5c384df7ba0b8d578a4c702b6bf1'
                            '1d5f OP_CHECKSIG'),
                    'hex': ('4104678afdb0fe5548271967f1a67130b7105cd6a8'
                            '28e03909a67962e0ea1f61deb649f6bc3f4cef38c4'
                            'f35504e51ec112de5c384df7ba0b8d578a4c702b6b'
                            'f11d5fac'),
                    'reqSigs': 1,
                    'type': 'pubkey',
                    'addresses': ['1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa']
                }
            }
        ]
    }

    def __init__(self):
        rpc = dict()
        rpc['username'] = _get_env('BOLTZMANN_RPC_USERNAME')
        rpc['password'] = _get_env('BOLTZMANN_RPC_PASSWORD')
        rpc['host'] = _get_env('BOLTZMANN_RPC_HOST')
        rpc['port'] = _get_env('BOLTZMANN_RPC_PORT')

        self._con = AuthServiceProxy(
            "http://{username}:{password}@{host}:{port}".format(**rpc))


    def _get_raw_tx(self, txid):
        """Returns the transaction in raw format."""
        if txid == ('4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7af'
                    'deda33b'):
            raise NoDataAvailableForGenesisBlockError()
        else:
            return self._con.getrawtransaction(txid)


    def _get_decoded_tx(self, txid):
        """Gets a human-readable string of the transaction in JSON format."""
        try:
            return self._con.getrawtransaction(txid, 1)
        except NoDataAvailableForGenesisBlockError:
            #bitcoind won't generate this, but here's what it would look like
            return self.GENESIS_BLOCK


    def _get_block_height(self, txid, rpc_tx=None):
        """Return the block height at which the transaction was mined.

        Args:
            txid (str)
            rpc_tx (Optional[dict]): The data for the specified transaction, if
                it has already been queried previously from the RPC interface.

        Raises: NoBlockHeightAvailableError: If no block height found.
        """
        best_block_hash = self._con.getbestblockhash()
        best_block = self._con.getblock(best_block_hash)
        best_block_height = best_block['height']

        if rpc_tx is None:
            rpc_tx = self._get_decoded_tx(txid)

        #ready for a fun hack? We can compute block height, but only if the
        #transaction in question has at least one unspent output.
        for idx, _ in enumerate(rpc_tx['vout']):
            #Find number of confirmations for this transaction
            txout = self._con.gettxout(txid, idx)
            if txout is not None:
                return best_block_height - txout['confirmations'] + 1

        warn("Could not find number of confirmations in any txo for {0}".format(
            txid))
        return -1

    def _get_output_address(self, prev_txid, output_index, prev_tx=None):
        """Get the address associated with the specified txo.

        Args:
            prev_txid (str): The id of the tx the output belongs to
            output_index (int): Index within the outputs corresponding to the
                output
            prev_tx (Optional[dict]): The RPC-style prev tx the output belongs
                to. If not specified, this will be fetched from the RPC
                interface.

        TODO: This does not properly handle multisig outputs that list multiple
        addresses per output.

        Raises: PrevOutAddressCannotBeDecodedError
        """
        if prev_tx is None:
            prev_tx = self._get_decoded_tx(prev_txid)

        if('vout' in prev_tx and len(prev_tx['vout']) > output_index and
           'scriptPubKey' in prev_tx['vout'][output_index]):
            if 'addresses' not in prev_tx['vout'][output_index]['scriptPubKey']:
                raise PrevOutAddressCannotBeDecodedError(
                    "Can't decode address for txo {0}:{1}".format(prev_txid,
                                                                  output_index))
            else:
                return ' '.join(prev_tx['vout'][output_index]['scriptPubKey']['addresses'])
        else:
            raise PrevOutAddressCannotBeDecodedError(
                ("Missing element for vout in get_output_address() with tx "
                 "id {0} and output index {1}").format(prev_txid, output_index))

    def _rpc_to_bci_input(self, rpc_input):
        """Convert RPC-style input to BCI-style input.

        Args:
            rpc_input (dict): The RPC-style representation of an input, found in
                a transaction's 'vin' array.

        Returns: dict: Representation of input, to be appended to a list
        attribute called 'inputs'. The input contains these fields:
            * 'prev_out' (dict)
                * 'tx_index' (None)
                * 'txid' (str): previous tx id
                * 'addr' (str)
                * 'n' (int): position of txo in prev tx
                * 'value' (int)
        """
        bci_input = dict()

        #do not create prev_out field if this input is part of a coinbase
        #  transaction. This is consistent with the BCI JSON format.
        if 'txid' in rpc_input:
            bci_input['prev_out'] = dict()
            bci_input['prev_out']['tx_index'] = None
            prev_txid = rpc_input['txid']
            prev_vout_num = rpc_input['vout'] #RPC field is ambiguously named :/
            bci_input['prev_out']['n'] = prev_vout_num

            prev_tx = self._get_decoded_tx(prev_txid)
            bci_input['prev_out']['addr'] = self._get_output_address(
                prev_txid, prev_vout_num, prev_tx)
            bci_input['prev_out']['script'] = (prev_tx['vout'][prev_vout_num]
                                               ['scriptPubKey']['hex'])
            float_val = prev_tx['vout'][prev_vout_num]['value']
            bci_input['prev_out']['value'] = _float_to_satoshi(float_val)
        return bci_input


    def get_tx(self, txid, testnet):
        """Get the `Transaction` object for specified hash.
        
        Testnet parameter isn't used.
        For now, we assume that a single bitcoind is running on the machine. 
        
        The `Transaction` constructors expects these fields for a dict:
            * 'block_height' (int)
            * 'time' (None)
            * 'hash' (str)
            * 'inputs' (List[dict]):
                * 'prev_out' (dict):
                    * 'n' (int)
                    * 'value' (int)
                    * 'addr' (str)
                    * 'tx_index' (None)
            * 'out' (List[dict]): same as 'prev_out'
        """
        rpc_style_tx = self._get_decoded_tx(txid)
        rpc_style_tx['block_height'] = self._get_block_height(txid, rpc_style_tx)
        rpc_style_tx['time'] = None
        rpc_style_tx['hash'] = rpc_style_tx['txid']

        rpc_style_tx['inputs'] = list()
        for txin in rpc_style_tx['vin']:
            inpt = self._rpc_to_bci_input(txin)
            rpc_style_tx['inputs'].append(inpt)

        rpc_style_tx['out'] = list()
        for txout in rpc_style_tx['vout']:
            outpt = _rpc_to_bci_output(txout)
            rpc_style_tx['out'].append(outpt)

        return Transaction(rpc_style_tx)

def _get_env(varname):
    val = os.getenv(varname, None)
    if val is None:
        raise MissingRPCConfigurationError('{0} is not set.'.format(varname))
    return str(val)

def _float_to_satoshi(float_val):
    """Convert value from BTC (decimal) to satoshis integer.
    This works fine on my machine in python3:
        >>> int(round(decimal.Decimal(0.00000001) * decimal.Decimal(1e8)))
        1
        >>> int(round(decimal.Decimal(87654321.12345678) * decimal.Decimal(1e8)))
        8765432112345678
    """
    return int(round(decimal.Decimal(float_val) * decimal.Decimal(1e8)))

def _rpc_to_bci_output(rpc_output):
    """Convert RPC-style otuput to BCI-style output.

    TODO: This does not properly handle multisig outputs that list multiple
    addresses per output.

    Args:
        rpc_output (dict): The RPC-style representation of an output, found
            in a tx's 'vout' array.

    Returns: dict: Representation of output, to be appended to a list
    attribute called 'out'. The output contains these fields:
        * 'tx_index' (None)
        * 'addr' (str)
        * 'value' (int)
        * 'n' (int)
    """
    bci_output = dict()
    bci_output['tx_index'] = None
    bci_output['n'] = rpc_output['n']
    bci_output['addr'] = ' '.join(rpc_output['scriptPubKey']['addresses'])
    bci_output['script'] = rpc_output['scriptPubKey']['hex']
    bci_output['value'] = _float_to_satoshi(rpc_output['value'])
    return bci_output
