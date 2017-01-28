'''
Created on 20160923
Based on original works done for OXT in January 2015
@author: LaurentMT
'''
import sys
from datetime import datetime
from collections import defaultdict
from boltzmann.linker.txos_linker import TxosLinker
from boltzmann.utils.lists import merge_sets


def process_tx(tx, options, max_duration, max_txos, max_cj_intrafees_ratio=0):
    '''
    Processes a transaction
    Parameters:
        tx                      = Transaction to be processed (@see boltzmann.utils.transaction.Transaction)
        options                 = options to be applied during processing
        max_duration            = max duration allocated to processing of a single tx (in seconds)
        max_txos                = max number of txos. Txs with more than max_txos inputs or outputs are not processed.
        max_cj_intrafees_ratio  = max intrafees paid by the taker of a coinjoined transaction. 
                                  Expressed as a percentage of the coinjoined amount.
    '''
    t1 = datetime.now()
    
    # Builds lists of filtered input/output txos (with generated ids)
    filtered_ins, map_ins = filter_txos(tx.inputs, 'I')
    filtered_outs, map_outs = filter_txos(tx.outputs, 'O')
    
    # Computes total input & output amounts + fees
    sum_inputs = sum([v[1] for v in filtered_ins])
    sum_outputs = sum([v[1] for v in filtered_outs])
    fees = sum_inputs - sum_outputs
    
    # Sets default intrafees paid by participants (fee_received_by_maker, fees_paid_by_taker)
    intrafees = (0, 0)
    
    # Processes the transaction
    if (len(filtered_ins) <= 1) or (len(filtered_outs) == 1):
        
        # Txs having no input (coinbase) or only 1 input/output (null entropy)
        # When entropy = 0, all inputs and outputs are linked and matrix is filled with 1.
        # No need to build this matrix. Every caller should be able to manage that.
        mat_lnk = None
        nb_cmbn = 1
        txo_ins = filtered_ins
        txo_outs = filtered_outs
    
    else:
        
        # Initializes the TxosLinker for this tx
        linker = TxosLinker(filtered_ins, filtered_outs, fees, max_duration, max_txos)
        
        # Computes a list of sets of inputs controlled by a same address
        linked_ins = get_linked_txos(filtered_ins, map_ins) if ('MERGE_INPUTS' in options) else []
        # Computes a list of sets of outputs controlled by a same address (not recommended)
        linked_outs = get_linked_txos(filtered_outs, map_outs) if ('MERGE_OUTPUTS' in options) else []
        
        # Computes intrafees to be used during processing
        if max_cj_intrafees_ratio > 0:
            # Computes a theoretic max number of participants
            ls_filtered_ins = [set([i[0]]) for i in filtered_ins]
            max_nb_ptcpts = len(merge_sets(linked_ins + ls_filtered_ins))
            # Checks if tx has a coinjoin pattern + gets estimated number of participants and coinjoined amount
            is_cj, nb_ptcpts, cj_amount = check_coinjoin_pattern(filtered_ins, filtered_outs, max_nb_ptcpts)
            # If coinjoin pattern detected, computes theoretic max intrafees
            if is_cj:
                intrafees = compute_coinjoin_intrafees(nb_ptcpts, cj_amount, max_cj_intrafees_ratio)
        
        # Computes entropy of the tx and txos linkability matrix
        (mat_lnk, nb_cmbn, txo_ins, txo_outs) = linker.process(linked_ins+linked_outs, options, intrafees)
        
    # Post processes results (replaces txo ids by bitcoin addresses)
    txo_ins = post_process_txos(txo_ins, map_ins)
    txo_outs = post_process_txos(txo_outs, map_outs)
    print('Duration = %s' % str( (datetime.now() - t1).total_seconds()))       
    return mat_lnk, nb_cmbn, txo_ins, txo_outs, fees, intrafees


def filter_txos(txos, prefix):
    '''
    Filters a list of txos by removing txos with null value (OP_RETURN, ...)
    Defines an id for each txo
    Returns:
        a list of tuples (txo_id, amount)
        a dict mapping txo ids to bitcoin addresses
    Parameters:
        txos = list of Txo objects (@see boltzmann.utils.transaction.Txo)
        prefix = a prefix to be used for ids generated
    '''
    filtered_txos = []
    map_id_addr = dict()
    
    for idx, txo in enumerate(txos):
        if txo.value > 0:
            txo_id = '%s%i' % (prefix, idx)
            filtered_txos.append((txo_id, txo.value))
            map_id_addr[txo_id] = txo.address
            
    return filtered_txos, map_id_addr

    
def get_linked_txos(txos, map_id_addr):
    '''
    Computes a list of sets of txos controlled by a same address
    Returns a list of sets of txo_ids [ {txo_id1, txo_id2, ...}, {txo_id3, txo_id4, ...} ]
    Parameters:
        txos         = list of txos (tuples (txo_id, amount))
        map_id_addr  = dictionary mapping txo_ids to addresses
    '''
    linked_txos = []
    
    for txo in txos:
        s_ins = { txo[0] }
        s_addr = { map_id_addr[txo[0]] }         
        # Checks if this set intersects with some set previously found
        for entry in linked_txos:
            k = entry[0]
            v = entry[1]
            if k & s_addr:
                # If an intersection is found, merges the 2 sets and removes previous set from linked_txos
                s_ins |= v
                s_addr |= k
                linked_txos.remove(entry)
        linked_txos.append((s_addr, s_ins))
    
    return [i[1] for i in linked_txos if len(i[1]) > 1]


def post_process_txos(txos, map_id_addr):
    '''
    Post processes a list of txos
    Basically replaces txo_id by associated bitcoin address
    Returns a list of txos (tuples (address, amount))
    Parameters:
        txos         = list of txos (tuples (txo_id, amount))
        map_id_addr  = dictionary mapping txo_ids to addresses
    '''
    return [(map_id_addr[txo[0]], txo[1]) for txo in txos if txo[0] in map_id_addr.keys()]



def check_coinjoin_pattern(txo_ins, txo_outs, max_nb_entities = sys.maxsize):
    '''
    Checks if a transaction looks like a coinjoin
    Returns a tuple (is_coinjoin, nb_participants, coinjoined_amount)
    Parameters:
        txo_ins           = list of inputs valves (tuples (tiid, amount))
        txo_outs          = list of outputs valves (tuples (tiid, amount))
        max_nb_entities   = estimated max number of entities participating in the coinjoin 
                            (info coming from a side channel source or from an analysis of tx structure)
    '''
    # Checks that we have more than 1 input entity
    if max_nb_entities < 2:
        return False, None, None
    
    # Computes a dictionary of #outputs per amount (d[amount] = nb_outputs)
    d_txo_outs = defaultdict(int)
    for txo in txo_outs:
        d_txo_outs[txo[1]] += 1
        
    # Computes #outputs
    nb_txo_outs = len(txo_outs) 
    
    # Tries to detect a coinjoin pattern in outputs:
    #   n outputs with same value, with n > 1
    #   nb_outputs <= 2*nb_ptcpts (with nb_ptcpts = min(n, max_nb_entities) )
    # If multiple candidate values 
    # selects option with max number of participants (and max amount as 2nd criteria)
    is_cj = False
    res_nb_ptcpts = 0
    res_amount = 0
    
    for k,v in d_txo_outs.items():
        if v > 1:
            max_nb_ptcpts = min(v, max_nb_entities)
            cond_txo_outs = nb_txo_outs <= 2 * max_nb_ptcpts
            cond_max_ptcpts = max_nb_ptcpts >= res_nb_ptcpts
            cond_max_amount = k > res_amount
            if cond_txo_outs and cond_max_ptcpts and cond_max_amount:
                is_cj = True
                res_nb_ptcpts = max_nb_ptcpts
                res_amount = k
      
    return is_cj, res_nb_ptcpts, res_amount


def compute_coinjoin_intrafees(nb_ptcpts, cj_amount, prct_max): 
    '''
    Computes theoretic intrafees involved in a coinjoin transaction (e.g. joinmarket)
    Returns a tuple (fee_received_by_maker, fees_paid_by_taker)
    Parameters:
        nb_ptcpts = number of participants
        cj_amount = common amount generated for the coinjoin transaction
        prct_max  = max percentage paid by the taker to all makers
    '''
    fee_maker = cj_amount * prct_max
    fee_taker = fee_maker * (nb_ptcpts - 1)
    return fee_maker, fee_taker



