'''
Created on 20160917
Based on original works done for OXT in January 2015
@author: LaurentMT
'''
import os
import math
import sys
from boltzmann.utils.tx_processor import compute_wallet_efficiency

# Adds boltzmann directory into path
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../../")

from boltzmann.linker.txos_linker import TxosLinker
from datetime import datetime


def build_test_vectors():
    test_vectors = []
    options = ['PRECHECK', 'LINKABILITY']

    # Test case A
    name = 'TEST A'
    inputs  = [ ('a', 10), ('b', 10) ]
    outputs = [ ('A', 8), ('B', 2), ('C', 3), ('D', 7) ]
    test_vectors.append((name, inputs, outputs, options))

    # Test case A with additional information (A & B controlled by same entity)
    name = 'TEST A with additional info'
    inputs  = [ ('a', 10), ('b', 10) ]
    outputs = [ ('A', 10), ('C', 3), ('D', 7) ]
    test_vectors.append((name, inputs, outputs, options))

    # Test case B
    name = 'TEST B'
    inputs  = [ ('a', 10), ('b', 10) ]
    outputs = [ ('A', 8), ('B', 2), ('C', 2), ('D', 8) ]
    test_vectors.append((name, inputs, outputs, options))

    # Test case B with additional information (A & B controlled by same entity)
    name = 'TEST B with additional info'
    inputs  = [ ('a', 10), ('b', 10) ]
    outputs = [ ('A', 10), ('C', 2), ('D', 8) ]
    test_vectors.append((name, inputs, outputs, options))

    # Test case C
    name = 'TEST C'
    inputs  = [ ('a', 10), ('b', 10) ]
    outputs = [ ('A', 5), ('B', 5), ('C', 5), ('D', 5) ]
    test_vectors.append((name, inputs, outputs, options))

    # Test case C with additional information (A & B controlled by same entity)
    name = 'TEST C with additional info'
    inputs  = [ ('a', 10), ('b', 10) ]
    outputs = [ ('A', 10), ('C', 5), ('D', 5) ]
    test_vectors.append((name, inputs, outputs, options))

    # Test case D
    name = 'TEST D'
    inputs  = [ ('a', 10), ('b', 10), ('c', 2) ]
    outputs = [ ('A', 8), ('B', 2), ('C', 2), ('D', 8), ('E', 2) ]
    test_vectors.append((name, inputs, outputs, options))

    # Test case P2 
    name = 'TEST P2'
    inputs  = [ ('a', 5), ('b', 5) ]
    outputs = [ ('A', 5), ('B', 5) ]
    test_vectors.append((name, inputs, outputs, options))

    # Test case P3 
    name = 'TEST P3'
    inputs  = [ ('a', 5), ('b', 5), ('c', 5) ]
    outputs = [ ('A', 5), ('B', 5), ('C', 5) ]
    test_vectors.append((name, inputs, outputs, options))

    # Test case P3 with fees
    name = 'TEST P3 with fees'
    inputs  = [ ('a', 5), ('b', 5), ('c', 5) ]
    outputs = [ ('A', 5), ('B', 3), ('C', 2) ]
    test_vectors.append((name, inputs, outputs, options))

    # Test case P3b
    name = 'TEST P3b'
    inputs  = [ ('a', 5), ('b', 5), ('c', 10) ]
    outputs = [ ('A', 5), ('B', 5), ('C', 10) ]
    test_vectors.append((name, inputs, outputs, options))

    # Test case P4 
    name = 'TEST P4'
    inputs  = [ ('a', 5), ('b', 5), ('c', 5), ('d', 5) ]
    outputs = [ ('A', 5), ('B', 5), ('C', 5), ('D', 5) ]
    test_vectors.append((name, inputs, outputs, options))

    # Test case P5 
    name = 'TEST P5'
    inputs  = [ ('a', 5), ('b', 5), ('c', 5), ('d', 5), ('e', 5) ]
    outputs = [ ('A', 5), ('B', 5), ('C', 5), ('D', 5), ('E', 5) ]
    test_vectors.append((name, inputs, outputs, options))

    # Test case P6 
    name = 'TEST P6'
    inputs  = [ ('a', 5), ('b', 5), ('c', 5), ('d', 5), ('e', 5), ('f', 5) ]
    outputs = [ ('A', 5), ('B', 5), ('C', 5), ('D', 5), ('E', 5), ('F', 5) ]
    test_vectors.append((name, inputs, outputs, options))

    # Test case P7 
    name = 'TEST P7'
    inputs  = [ ('a', 5), ('b', 5), ('c', 5), ('d', 5), ('e', 5), ('f', 5), ('g', 5) ]
    outputs = [ ('A', 5), ('B', 5), ('C', 5), ('D', 5), ('E', 5), ('F', 5), ('G', 5) ]
    test_vectors.append((name, inputs, outputs, options))

    # Test case P8 
    name = 'TEST P8'
    inputs  = [ ('a', 5), ('b', 5), ('c', 5), ('d', 5), ('e', 5), ('f', 5), ('g', 5), ('h', 5) ]
    outputs = [ ('A', 5), ('B', 5), ('C', 5), ('D', 5), ('E', 5), ('F', 5), ('G', 5), ('H', 5) ]
    test_vectors.append((name, inputs, outputs, options))

    # Test case P9 
    name = 'TEST P9'
    inputs  = [ ('a', 5), ('b', 5), ('c', 5), ('d', 5), ('e', 5), ('f', 5), ('g', 5), ('h', 5), ('i', 5) ]
    outputs = [ ('A', 5), ('B', 5), ('C', 5), ('D', 5), ('E', 5), ('F', 5), ('G', 5), ('H', 5), ('I', 5) ]
    test_vectors.append((name, inputs, outputs, options))

    # Test case P10 
    name = 'TEST P10'
    inputs  = [ ('a', 5), ('b', 5), ('c', 5), ('d', 5), ('e', 5), ('f', 5), ('g', 5), ('h', 5), ('i', 5), ('j', 5) ]
    outputs = [ ('A', 5), ('B', 5), ('C', 5), ('D', 5), ('E', 5), ('F', 5), ('G', 5), ('H', 5), ('I', 5), ('J', 5) ]
    test_vectors.append((name, inputs, outputs, options))

    return test_vectors


def process_test(inputs, outputs, options, max_duration):
    t1 = datetime.now()
    sum_inputs = sum([v[1] for v in inputs])
    sum_outputs = sum([v[1] for v in outputs])
    fees = sum_inputs - sum_outputs

    linker = TxosLinker(inputs, outputs, fees, max_duration)
    (mat_lnk, nb_cmbn, inputs, outputs) = linker.process(options=options)

    print('Duration = %s' % str( (datetime.now() - t1).total_seconds()))
    return mat_lnk, nb_cmbn, inputs, outputs, fees


def display_results(mat_lnk, nb_cmbn, inputs, outputs, fees, efficiency):
    print('\nInputs = ' + str(inputs))
    print('\nOutputs = ' + str(outputs))
    print('\nFees = %i' % fees)

    print('\nNb combinations = %i' % nb_cmbn)
    if nb_cmbn > 0:
        print('Tx entropy = %f' % math.log2(nb_cmbn))

    if efficiency is not None and efficiency > 0:
        print('Wallet efficiency = %f%% (%f bits)' % (efficiency*100, math.log2(efficiency)))            

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



if __name__ == '__main__':

    max_duration_test = 600

    # Builds test vectors
    test_vectors = build_test_vectors()

    for test in test_vectors:
        test_name = test[0]
        print('\n\n--- %s -------------------------------------' % test_name)

        # Processes the test
        (mat_lnk, nb_cmbn, inputs, outputs, fees) = process_test(test[1], test[2], test[3], max_duration_test)
        # Computes the wallet efficiency
        efficiency = compute_wallet_efficiency(len(test[1]), len(test[2]), nb_cmbn)
        # Displays the results
        display_results(mat_lnk, nb_cmbn, inputs, outputs, fees, efficiency)
