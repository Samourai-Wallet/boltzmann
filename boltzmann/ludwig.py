'''
Created on 20160917
@author: LaurentMT
'''
import os
import math
import getopt
from datetime import datetime

import sys
# Adds boltzmann directory into path
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")

from boltzmann.utils.bci_wrapper import BlockchainInfoWrapper
from boltzmann.linker.txos_linker import TxosLinker


def process_tx(tx, options, max_duration):
    t1 = datetime.now()
    
    inputs = [(txo_in.address, txo_in.value) for txo_in in tx.inputs]
    outputs = [(txo_out.address, txo_out.value) for txo_out in tx.outputs]
    
    sum_inputs = sum([v[1] for v in inputs])
    sum_outputs = sum([v[1] for v in outputs])
    fees = sum_inputs - sum_outputs
    
    linker = TxosLinker(inputs, outputs, fees, max_duration)
    (mat_lnk, nb_cmbn, inputs, outputs) = linker.process(options=options)
    
    print('Duration = %s' % str( (datetime.now() - t1).total_seconds()))
    return mat_lnk, nb_cmbn, inputs, outputs, fees



def display_results(mat_lnk, nb_cmbn, inputs, outputs, fees):
    print('\nInputs = ' + str(inputs))
    print('\nOutputs = ' + str(outputs))
    print('\nFees = %i' % fees)
    
    print('\nNb combinations = %i' % nb_cmbn)
    if nb_cmbn > 0:
        print('Tx entropy = %f' % math.log2(nb_cmbn))
    
    if mat_lnk is not None:
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
    



def main(txids, options=['PRECHECK', 'LINKABILITY'], max_duration=600):
    '''
    Main function
    Parameters:
        txids = list of transactions txids to be processed
    '''
    # Initializes the wrapper for bci api
    bci_wrapper = BlockchainInfoWrapper()
    
    for txid in txids:
        print('\n\n--- %s -------------------------------------' % txid)
        
        # Retrieves the tx from bci
        try:
            tx = bci_wrapper.get_tx(txid)
        except:
            print('Unable to retrieve information for %s from bc.i' % txid)
            continue
        
        # Computes the entropy of the tx and the linkability of txos
        (mat_lnk, nb_cmbn, inputs, outputs, fees) = process_tx(tx, options, max_duration)
        # Displays the results
        display_results(mat_lnk, nb_cmbn, inputs, outputs, fees)
        
    

def usage():
    '''
    Usage message for this module
    '''
    sys.stdout.write('python ludwig.py [--duration=600] [--options=PRECHECK,LINKABILITY,MERGE_FEES] [--txids=8e56317360a548e8ef28ec475878ef70d1371bee3526c017ac22ad61ae5740b8,812bee538bd24d03af7876a77c989b2c236c063a5803c720769fc55222d36b47,...]\n'); 
    sys.stdout.flush()
    

if __name__ == '__main__':
    # Initializes parameters
    txids = []
    max_duration = 600
    options = ['PRECHECK', 'LINKABILITY']
    argv = sys.argv[1:]
    # Processes arguments
    try:                                
        opts, args = getopt.getopt(argv, 'ht:d:o:', ['help', 'txids=', 'duration=', 'options='])
    except getopt.GetoptError:          
        usage()                         
        sys.exit(2)                     
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()                     
            sys.exit()
        elif opt in ('-d', '--duration'):
            max_duration = int(arg)   
        elif opt in ('-t', '--txids'):
            txids = [t for t in arg.split(',')]
        elif opt in ('-o', '--options'):
            options = [t for t in arg.split(',')]
    # Processes computations
    main(txids, options, max_duration)
                