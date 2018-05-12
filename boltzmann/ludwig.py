'''
Created on 20160917
@author: LaurentMT
'''
import os
import math
import getopt
import traceback
import sys

# Adds boltzmann directory into path
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")

from boltzmann.utils.tx_processor import process_tx
from boltzmann.utils.bitcoind_rpc_wrapper import BitcoindRPCWrapper
from boltzmann.utils.bci_wrapper import BlockchainInfoWrapper
from boltzmann.utils.smartbit_wrapper import SmartbitWrapper



def display_results(mat_lnk, nb_cmbn, inputs, outputs, fees, intrafees, efficiency):
    '''
    Displays the results for a given transaction
    Parameters:
        mat_lnk   = linkability matrix
        nb_cmbn   = number of combinations detected
        inputs    = list of input txos (tuples (address, amount))
        outputs   = list of output txos (tuples (address, amount))
        fees      = fees associated to this transaction
        intrafees = max intrafees paid/received by participants (tuple (max intrafees received, max intrafees paid))
        efficiency= wallet efficiency for this transaction (expressed as a percentage)
    '''
    print('\nInputs = ' + str(inputs))
    print('\nOutputs = ' + str(outputs))
    print('\nFees = %i satoshis' % fees)

    if (intrafees[0] > 0) and (intrafees[1] > 0):
        print('\nHypothesis: Max intrafees received by a participant = %i satoshis' % intrafees[0])
        print('Hypothesis: Max intrafees paid by a participant = %i satoshis' % intrafees[1])

    print('\nNb combinations = %i' % nb_cmbn)
    if nb_cmbn > 0:
        print('Tx entropy = %f bits' % math.log2(nb_cmbn))

    if efficiency is not None and efficiency > 0:
        print('Wallet efficiency = %f%% (%f bits)' % (efficiency*100, math.log2(efficiency)))

    if mat_lnk is None:
        if nb_cmbn == 0:
            print('\nSkipped processing of this transaction (too many inputs and/or outputs)')
    else:
        if nb_cmbn != 0:
            print('\nLinkability Matrix (probabilities) :')
            print(mat_lnk / nb_cmbn)
        else:
            print('\nLinkability Matrix (#combinations with link) :')
            print(mat_lnk)

        print('\nDeterministic links :')
        for i in range(0, len(outputs)):
            for j in range(0, len(inputs)):
                if (mat_lnk[i,j] == nb_cmbn) and mat_lnk[i,j] != 0 :
                    print('%s & %s are deterministically linked' % (inputs[j], outputs[i]))




def main(txids, rpc, testnet, smartbit, options=['PRECHECK', 'LINKABILITY', 'MERGE_INPUTS'], max_duration=600, max_txos=12, max_cj_intrafees_ratio=0):
    '''
    Main function
    Parameters:
        txids                   = list of transactions txids to be processed
        rpc                     = use bitcoind's RPC interface (or blockchain.info web API)
        testnet                 = use testnet (blockchain.info by default)
        smartbit                = use smartbit data provider
        options                 = options to be applied during processing
        max_duration            = max duration allocated to processing of a single tx (in seconds)
        max_txos                = max number of txos. Txs with more than max_txos inputs or outputs are not processed.
        max_cj_intrafees_ratio  = max intrafees paid by the taker of a coinjoined transaction.
                                  Expressed as a percentage of the coinjoined amount.
    '''
    blockchain_provider = None
    provider_descriptor = ''
    if rpc:
        blockchain_provider = BitcoindRPCWrapper()
        provider_descriptor = 'local RPC interface'
        testnet = ()
    else:
        if smartbit == True:
            blockchain_provider = SmartbitWrapper()
            provider_descriptor = 'remote Smartbit API'
        else:
            blockchain_provider = BlockchainInfoWrapper()
            provider_descriptor = 'remote blockchain.info API'

    print("DEBUG: Using %s" % provider_descriptor)

    for txid in txids:
        print('\n\n--- %s -------------------------------------' % txid)
        # retrieves the tx from local RPC or external data provider
        try:
            tx = blockchain_provider.get_tx(txid, *testnet)
            print("DEBUG: Tx fetched: {0}".format(str(tx)))
        except Exception as err:
            print('Unable to retrieve information for %s from %s: %s %s' % (txid, provider_descriptor, err, traceback.format_exc()))
            continue

        # Computes the entropy of the tx and the linkability of txos
        (mat_lnk, nb_cmbn, inputs, outputs, fees, intrafees, efficiency) = process_tx(tx, options, max_duration, max_txos, max_cj_intrafees_ratio)

        # Displays the results
        display_results(mat_lnk, nb_cmbn, inputs, outputs, fees, intrafees, efficiency)



def usage():
    '''
    Usage message for this module
    '''
    sys.stdout.write('python ludwig.py [--rpc] [--testnet] [--smartbit] [--duration=600] [--maxnbtxos=12] [--cjmaxfeeratio=0] [--options=PRECHECK,LINKABILITY,MERGE_FEES,MERGE_INPUTS,MERGE_OUTPUTS] [--txids=8e56317360a548e8ef28ec475878ef70d1371bee3526c017ac22ad61ae5740b8,812bee538bd24d03af7876a77c989b2c236c063a5803c720769fc55222d36b47,...]');
    sys.stdout.write('\n\n[-t OR --txids] = List of txids to be processed.')
    sys.stdout.write('\n\n[-p OR --rpc] = Use bitcoind\'s RPC interface as source of blockchain data')
    sys.stdout.write('\n\n[-T OR --testnet] = Use testnet interface as source of blockchain data')
    sys.stdout.write('\n\n[-s OR --smartbit] = Use Smartbit interface as source of blockchain data')
    sys.stdout.write('\n\n[-d OR --duration] = Maximum number of seconds allocated to the processing of a single transaction. Default value is 600')
    sys.stdout.write('\n\n[-x OR --maxnbtxos] = Maximum number of inputs or ouputs. Transactions with more than maxnbtxos inputs or outputs are not processed. Default value is 12.')
    sys.stdout.write('\n\n[-r OR --cjmaxfeeratio] = Max intrafees paid by the taker of a coinjoined transaction. Expressed as a percentage of the coinjoined amount. Default value is 0.')

    sys.stdout.write('\n\n[-o OR --options] = Options to be applied during processing. Default value is PRECHECK, LINKABILITY, MERGE_INPUTS')
    sys.stdout.write('\n    Available options are :')
    sys.stdout.write('\n    PRECHECK = Checks if deterministic links exist without processing the entropy of the transaction. Similar to Coinjoin Sudoku by K.Atlas.')
    sys.stdout.write('\n    LINKABILITY = Computes the entropy of the transaction and the txos linkability matrix.')
    sys.stdout.write('\n    MERGE_INPUTS = Merges inputs "controlled" by a same address. Speeds up computations.')
    sys.stdout.write('\n    MERGE_OUTPUTS = Merges outputs "controlled" by a same address. Speeds up computations but this option is not recommended.')
    sys.stdout.write('\n    MERGE_FEES = Processes fees as an additional output paid by a single participant. May speed up computations.')
    sys.stdout.flush()


if __name__ == '__main__':
    # Initializes parameters
    txids = []
    max_txos = 12
    max_duration = 600
    max_cj_intrafees_ratio = 0 #0.005
    options = ['PRECHECK', 'LINKABILITY', 'MERGE_INPUTS']
    argv = sys.argv[1:]
    # Processes arguments
    try:
        opts, args = getopt.getopt(argv, 'hpt:p:T:s:d:o:r:x:', ['help', 'rpc', 'testnet', 'smartbit', 'txids=', 'duration=', 'options=', 'cjmaxfeeratio=', 'maxnbtxos='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    rpc = False
    testnet = False
    smartbit = False
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt in ('-p', '--rpc'):
            rpc = True
        elif opt in ('-T', '--testnet'):
            testnet = True
        elif opt in ('-s', '--smartbit'):
            smartbit = True
        elif opt in ('-d', '--duration'):
            max_duration = int(arg)
        elif opt in ('-x', '--maxnbtxos'):
            max_txos = int(arg)
        elif opt in ('-r', '--cjmaxfeeratio'):
            max_cj_intrafees_ratio = float(arg)
        elif opt in ('-t', '--txids'):
            txids = [t.strip() for t in arg.split(',')]
        elif opt in ('-o', '--options'):
            options = [t.strip() for t in arg.split(',')]
    # Processes computations
    main(txids=txids, rpc=rpc, testnet=testnet, smartbit=smartbit, options=options, max_duration=max_duration, max_txos=max_txos, max_cj_intrafees_ratio=max_cj_intrafees_ratio)
