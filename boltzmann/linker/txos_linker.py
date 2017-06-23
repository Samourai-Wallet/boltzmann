'''
Created on 20160917
Based on original works done for OXT in January 2015
@author: LaurentMT
'''
import numpy as np
from datetime import datetime
from collections import deque, defaultdict
from sortedcontainers.sortedlist import SortedList
from boltzmann.utils.lists import merge_sets
import sys


class TxosLinker(object):
    '''
    A class allowing to compute the entropy of Bitcoin transactions
    and the linkability of inputs/outputs of a transaction
    '''

    '''
    CONSTANTS
    '''
    # Default maximum duration in seconds
    MAX_DURATION = 180

    # Processing options
    LINKABILITY = 'LINKABILITY'
    PRECHECK = 'PRECHECK'
    MERGE_FEES = 'MERGE_FEES'

    # Markers
    FEES = 'FEES'
    PACK = 'PACK'

    # Max number of inputs (or outputs) which can be processed by this algorithm
    MAX_NB_TXOS = 12



    '''
    ATTRIBUTES

    # List of input txos expressed as tuples (id, amount)
    inputs = []

    # List of output txos expressed as tuples (id, amount)
    outputs = []

    # Fees associated to the transaction
    fees = 0

    # Matrix of txos linkability
    #    Columns = input txos
    #    Rows = output txos
    #    Cells = number of combinations for which an input and an output are linked
    links = np.array()

    # Number of valid transactions combinations
    nb_tx_cmbn = 0

    # Maximum duration of the script (in seconds)
    _max_duration = MAX_DURATION
    '''


    '''
    INITIALIZATION
    '''
    def __init__(self, inputs=[], outputs=[], fees=0, max_duration=MAX_DURATION, max_txos=MAX_NB_TXOS):
        '''
        Constructor
        Parameters:
            inputs       = list of inputs txos [(v1_id, v1_amount), ...]
            outputs      = list of outputs txos [(v1_id, v1_amount), ...]
            fees         = amount of fees associated to the transaction
            max_duration = max duration allocated to processing of a single tx (in seconds)
            max_txos     = max number of txos. Txs with more than max_txos inputs or outputs are not processed.
        '''
        self._orig_ins = inputs
        self._orig_outs = outputs
        self._orig_fees = fees
        self._max_duration = max_duration
        self.max_txos = max_txos
        self._packs = []


    '''
    PUBLIC METHODS
    '''
    def process(self, linked_txos=[], options=[LINKABILITY, PRECHECK], intrafees=(0,0)):
        '''
        Computes the linkability between a set of input txos and a set of output txos
        Returns:
            linkability matrix
            number of possible combinations for the transaction
            list of inputs (sorted by decreasing value)
            list of outputs (sorted by decreasing value)
        Parameters:
            linked_txos     = list of sets storing linked input txos. Each txo is identified by its id
            options         = list of actions to be applied
                LINKABILITY : computes the linkability matrix
                PRECHECK    : prechecks existence of deterministic links between inputs and outputs
                MERGE_FEES  : consider that all fees have been paid by a unique sender and manage fees as an additionnal output
            intrafees       = tuple (fees_maker, fees_taker) of max "fees" paid among participants
                              used for joinmarket transactions
                              fees_maker are potential max "fees" received by a participant from another participant
                              fees_taker are potential max "fees" paid by a participant to all others participants
        '''
        self._options = options
        self.inputs = self._orig_ins.copy()
        self.outputs = self._orig_outs.copy()
        self._fees_maker = intrafees[0]
        self._fees_taker = intrafees[1]
        self._has_intrafees = True if (self._fees_maker or self._fees_taker) else False

        # Packs txos known as being controlled by a same entity
        # It decreases the entropy and speeds-up computations
        if linked_txos:
            self._pack_linked_txos(linked_txos)

        # Manages fees
        if (self.MERGE_FEES in options) and (self._orig_fees > 0):
            # Manages fees as an additional output (case of sharedsend by blockchain.info).
            # Allows to reduce the volume of computations to be done.
            self._fees = 0
            txo_fees = (self.FEES, self._orig_fees)
            self.outputs.append(txo_fees)
        else:
            self._fees = self._orig_fees

        # Checks deterministic links
        nb_cmbn = 0
        if self.PRECHECK in options and self._check_limit_ok(self.PRECHECK) and (not self._has_intrafees):
            # Prepares the data
            self._prepare_data()
            self._match_agg_by_val()
            # Checks deterministic links
            dtrm_lnks, dtrm_lnks_id = self._check_dtrm_links()
            # If deterministic links have been found, fills the linkability matrix
            # (returned as result if linkability is not processed)
            if dtrm_lnks is not None:
                shape = ( len(self.outputs), len(self.inputs) )
                mat_lnk = np.zeros(shape, dtype=np.int64)
                for (r,c) in dtrm_lnks:
                    mat_lnk[r,c] = 1
        else:
            mat_lnk = None
            dtrm_lnks_id = None

        # Checks if all inputs and outputs have already been merged
        nb_ins = len(self.inputs)
        nb_outs = len(self.outputs)
        if (nb_ins == 0) or (nb_outs == 0):
            nb_cmbn = 1
            shape = (nb_outs, nb_ins)
            mat_lnk = np.ones(shape, dtype=np.int64)
        elif self.LINKABILITY in options and self._check_limit_ok(self.LINKABILITY):
            # Packs deterministic links if needed
            if dtrm_lnks_id is not None:
                dtrm_lnks_id = [set(lnk) for lnk in dtrm_lnks_id]
                self._pack_linked_txos(dtrm_lnks_id)
            # Prepares data
            self._prepare_data()
            self._match_agg_by_val()
            # Computes a matrix storing a tree composed of valid pairs of input aggregates
            self._compute_in_agg_cmbn()
            # Builds the linkability matrix
            nb_cmbn, mat_lnk = self._compute_link_matrix()

        # Unpacks the matrix
        mat_lnk = self._unpack_link_matrix(mat_lnk, nb_cmbn)

        # Returns results
        return mat_lnk, nb_cmbn, self.inputs, self.outputs


    '''
    PREPARATION
    '''
    def _prepare_data(self):
        '''
        Computes several data structures which will be used later
        Parameters:
            inputs  = list of input txos
            outputs = list of output txos
        '''
        # Prepares data related to the input txos
        self.inputs,\
        self._all_in_agg,\
        self._all_in_agg_val = self._prepare_txos(self.inputs)

        # Prepares data related to the output txos
        self.outputs,\
        self._all_out_agg,\
        self._all_out_agg_val = self._prepare_txos(self.outputs)


    def _prepare_txos(self, txos):
        '''
        Computes several data structures related to a list of txos
        Returns:
            list of txos sorted by decreasing values
            array of aggregates (combinations of txos) in binary format
            array of values associated to the aggregates
        Parameters:
            txos = list of txos (list of tuples (id, value))
        '''
        # Removes txos with null value
        txos = filter(lambda x: x[1] > 0, txos)

        # Orders txos by value
        txos = sorted(txos, key=lambda tup: tup[1], reverse=True)

        # Creates a 1D array of values
        vals = [ e[1] for _, e in enumerate(txos) ]
        all_val = np.array(vals, dtype='int64')

        # Computes all possible combinations of txos encoded in binary format
        expnt = len(txos)
        shape = (expnt, 2**expnt)
        all_agg = np.zeros(shape, dtype=np.bool)
        base = np.array([0,1], dtype=bool)

        for j in range(0, expnt):
            two_exp_j = 2**j
            tmp = np.repeat(base, two_exp_j)
            all_agg[j, :] = np.tile(tmp, int(2**(expnt-1) / two_exp_j))
        #all_agg = np.arange(2**expnt) >> np.arange(expnt)[::, np.newaxis] & 1

        # Computes values of aggregates
        all_agg_val = np.dot(all_val, all_agg)

        # Returns computed data structures
        return txos, all_agg, all_agg_val


    '''
    PROCESSING OF AGGREGATES
    '''
    def _match_agg_by_val(self):
        '''
        Matches input/output aggregates by values and returns a bunch of data structs
        '''
        self._all_match_in_agg = SortedList()
        self._match_in_agg_to_val = defaultdict(int)
        self._val_to_match_out_agg = defaultdict(set)

        # Gets unique values of input / output aggregates
        all_unique_in_agg_val, _ = np.unique(self._all_in_agg_val, return_inverse=True)
        all_unique_out_agg_val, _ = np.unique(self._all_out_agg_val, return_inverse=True)

        # Computes total fees paid/receiver by taker/maker
        if self._has_intrafees:
            fees_taker = self._fees + self._fees_taker
            fees_maker = - self._fees_maker         # doesn't take into account tx fees paid by makers

        # Finds input and output aggregates with matching values
        for in_agg_val in np.nditer(all_unique_in_agg_val):
            val = int(in_agg_val)

            for out_agg_val in np.nditer(all_unique_out_agg_val):

                diff = in_agg_val - out_agg_val

                if (not self._has_intrafees) and (diff < 0):
                    break
                else:
                    # Computes conditions required for a matching
                    cond_no_intrafees = (not self._has_intrafees) and diff <= self._fees
                    cond_intrafees = self._has_intrafees and\
                                     ( (diff <= 0 and diff >= fees_maker) or (diff >= 0 and diff <= fees_taker) )

                    if cond_no_intrafees or cond_intrafees:
                        # Registers the matching input aggregate
                        match_in_agg = np.where(self._all_in_agg_val == in_agg_val)[0]

                        for in_idx in match_in_agg:
                            if not in_idx in self._all_match_in_agg:
                                self._all_match_in_agg.add(in_idx)
                                self._match_in_agg_to_val[in_idx] = val

                        # Registers the matching output aggregate
                        match_out_agg = np.where(self._all_out_agg_val == out_agg_val)[0]
                        self._val_to_match_out_agg[val].update(match_out_agg.tolist())


    def _compute_in_agg_cmbn(self):
        '''
        Computes a matrix of valid combinations (pairs) of input aggregates
        Returns a dictionary (parent_agg => (child_agg1, child_agg2))
        We have a valid combination (agg1, agg2) if:
           R1/ child_agg1 & child_agg2 = 0 (no bitwise overlap)
           R2/ child_agg1 > child_agg2 (matrix is symmetric)
        '''
        aggs = self._all_match_in_agg[1:-1]
        tgt = self._all_match_in_agg[-1]
        mat = defaultdict(list)
        saggs = set(aggs)

        for i in range(0, tgt+1):
            if i in saggs:
                j_max = min(i, tgt - i + 1)
                for j in range(0, j_max):
                    if (i & j == 0) and (j in saggs):
                        mat[i+j].append( (i,j) )
        self._mat_in_agg_cmbn = mat


    '''
    COMPUTATION OF LINKS BETWEEN TXOS
    '''
    def _check_dtrm_links(self):
        '''
        Checks the existence of deterministic links between inputs and outputs
        Returns a list of tuples (idx_output, idx_input) and a list of tuples (id_output, id_input)
        '''
        nb_ins = len(self.inputs)
        nb_outs = len(self.outputs)

        shape = (nb_outs, nb_ins)
        mat_cmbn = np.zeros(shape, dtype=np.int64)

        shape = (1, nb_ins)
        in_cmbn = np.zeros(shape, dtype=np.int64)

        # Computes a matrix storing numbers of raw combinations matching input/output pairs
        # Also computes sum of combinations along inputs axis to get the number of combinations
        for (in_idx, val) in self._match_in_agg_to_val.items():
            for out_idx in self._val_to_match_out_agg[val]:
                mat_cmbn += self._get_link_cmbn(in_idx, out_idx)
                in_cmbn += self._all_in_agg[:,in_idx][np.newaxis,:]

        # Builds a list of sets storing inputs having a deterministic link with an output
        nb_cmbn = in_cmbn[0,0]
        dtrm_rows, dtrm_cols = np.where(mat_cmbn == nb_cmbn)
        dtrm_coords = list(zip(dtrm_rows, dtrm_cols))
        dtrm_aggs = [(self.outputs[o][0], self.inputs[i][0]) for (o,i) in dtrm_coords]
        return dtrm_coords, dtrm_aggs


    def _compute_link_matrix(self):
        '''
        Computes the linkability matrix
        Returns the number of possible combinations and the links matrix
        Implements a depth-first traversal of the inputs combinations tree (right to left)
        For each input combination we compute the matching output combinations.
        This is a basic brute-force solution. Will have to find a better method later.
        '''
        nb_tx_cmbn = 0
        itgt = 2 ** len(self.inputs) - 1
        otgt = 2 ** len(self.outputs) - 1
        d_links = defaultdict(int)

        # Initializes a stack of tasks & sets the initial task
        #  0: index used to resume the processing of the task (required for depth-first algorithm)
        #  1: il = left input aggregate
        #  2: ir = right input aggregate
        #  3: d_out = outputs combination matching with current input combination
        #             dictionary of dictionary :  { or =>  { ol => (nb_parents_cmbn, nb_children_cmbn) } }
        stack = deque()
        ini_d_out = defaultdict(dict)
        ini_d_out[otgt] = { 0: (1, 0) }
        stack.append( (0, 0, itgt, ini_d_out) )

        # Sets start date/hour
        start_time = datetime.now()

        # Iterates over all valid inputs combinations (top->down)
        while len(stack) > 0:
            # Checks duration
            curr_time = datetime.now()
            delta_time = curr_time - start_time
            if delta_time.total_seconds() >= self._max_duration:
                return 0, None

            # Gets data from task
            t = stack[-1]
            idx_il = t[0]
            il = t[1]
            ir = t[2]
            d_out = t[3]
            n_idx_il = idx_il

            # Gets all valid decompositions of right input aggregate
            ircs = self._mat_in_agg_cmbn[ir]
            len_ircs = len(ircs)

            for i in range(idx_il, len_ircs):

                n_idx_il = i
                n_d_out = defaultdict(dict)

                # Gets left input sub-aggregate (column from ircs)
                n_il = ircs[i][1]

                # Checks if we must process this pair (columns from ircs are sorted in decreasing order)
                if n_il > il:
                    # Gets the right input sub-aggregate (row from ircs)
                    n_ir = ircs[i][0]

                    # Iterates over outputs combinations previously found
                    for o_r in d_out:
                        sol = otgt - o_r
                        # Computes the number of parent combinations
                        nb_prt = sum([s[0] for s in d_out[o_r].values()])

                        # Iterates over output sub-aggregates matching with left input sub-aggregate
                        val_il = self._match_in_agg_to_val[n_il]
                        for n_ol in self._val_to_match_out_agg[val_il]:

                            # Checks compatibility of output sub-aggregate with left part of output combination
                            if (sol & n_ol == 0):
                                # Computes:
                                #   the sum corresponding to the left part of the output combination
                                #   the complementary right output sub-aggregate
                                n_sol = sol + n_ol
                                n_or = otgt - n_sol
                                # Checks if the right output sub-aggregate is valid
                                val_ir = self._match_in_agg_to_val[n_ir]
                                match_out_agg = self._val_to_match_out_agg[val_ir]
                                # Adds this output combination into n_d_out if all conditions met
                                if (n_sol & n_or == 0) and (n_or in match_out_agg):
                                    n_d_out[n_or][n_ol] = (nb_prt, 0)

                    # Updates idx_il for the current task
                    stack[-1] = (i + 1, il, ir, d_out)
                    # Pushes a new task which will decompose the right input aggregate
                    stack.append( (0, n_il, n_ir, n_d_out) )
                    # Executes the new task (depth-first)
                    break

                else:
                    # No more results for il, triggers a break and a pop
                    n_idx_il = len_ircs
                    break

            # Checks if task has completed
            if n_idx_il > len_ircs - 1:
                # Pops the current task
                t = stack.pop()
                il = t[1]
                ir = t[2]
                d_out = t[3]

                # Checks if it's the root task
                if len(stack) == 0:
                    # Retrieves the number of combinations from root task
                    nb_tx_cmbn = d_out[otgt][0][1]

                else:
                    # Gets parent task
                    p_t = stack[-1]
                    p_d_out = p_t[3]

                    # Iterates over all entries from d_out
                    for (o_r, l_ol) in d_out.items():
                        r_key = (ir, o_r)
                        # Iterates over all left aggregates
                        for (ol, (nb_prnt, nb_chld)) in l_ol.items():
                            l_key = (il, ol)
                            # Updates the dictionary of links for the pair of aggregates
                            nb_occur = nb_chld + 1
                            d_links[r_key] += nb_prnt
                            d_links[l_key] += nb_prnt * nb_occur
                            # Updates parent d_out by back-propagating number of child combinations
                            p_or = ol + o_r
                            p_l_ol = p_d_out[p_or]
                            for (p_ol, (p_nb_prt, p_nb_chld)) in p_l_ol.items():
                                p_d_out[p_or][p_ol] = (p_nb_prt, p_nb_chld + nb_occur)

        # Fills the matrix
        links = self._get_link_cmbn(itgt, otgt)
        nb_tx_cmbn += 1
        for (lnk, mult) in d_links.items():
            links = links + self._get_link_cmbn(lnk[0], lnk[1]) * mult

        return nb_tx_cmbn, links


    def _get_link_cmbn(self, in_agg, out_agg):
        '''
        Computes a linkability matrix encoding the matching of given input/output aggregates
        Returns a numpy array
        Parameters:
            in_agg     = input aggregate
            out_agg    = output aggregate
        '''
        vouts = self._all_out_agg[:,out_agg][:,np.newaxis]
        vins = self._all_in_agg[:,in_agg][np.newaxis,:]
        return np.dot(vouts, vins)


    '''
    PACKING/UNPACKING OF LINKED TXOS
    '''
    def _pack_linked_txos(self, linked_txos):
        '''
        Packs input txos which are known as being controlled by a same entity
        Parameters:
            linked_txos = list of sets storing linked input txos. Each txo is identified by its "id"
        '''
        idx = len(self._packs)

        # Merges packs sharing common elements
        packs = merge_sets(linked_txos)

        for pack in packs:
            ins = []
            val_ins = 0

            for i in self.inputs:
                if i[0] in pack:
                    ins.append(i)
                    val_ins += i[1]

            idx += 1
            if len(ins) > 0:
                lbl = '%s_I%i' % (self.PACK, idx)
                inp = (lbl, val_ins)
                self.inputs.append(inp)
                in_pack = (lbl, val_ins, 'INPUTS', ins, [])
                self._packs.append(in_pack)
                [self.inputs.remove(v) for v in ins]


    def _unpack_link_matrix(self, mat_lnk, nb_cmbn):
        '''
        Unpacks linked txos in the linkability matrix
        Returns the unpacked matrix
        Parameters:
            mat_lnk = linkability matrix to be unpacked
            nb_cmbn = number of combinations associated to the linkability matrix
        '''
        mat_res = mat_lnk
        nb_cmbn = max(1, nb_cmbn)

        for (pack, val, lctn, ins, outs) in reversed(self._packs):

            if lctn == 'INPUTS':
                key = (pack, val)
                idx = self.inputs.index(key)
                if mat_lnk is not None:
                    nb_ins = len(ins)
                    nb_outs = len(self.outputs)
                    # Inserts columns into the matrix for packed inputs
                    shape = (nb_outs, nb_ins)
                    vals = np.zeros(shape , dtype=np.int64)
                    vals += mat_res[:,idx][:, np.newaxis]
                    mat_res = np.hstack( (mat_res[:,0:idx], vals, mat_res[:,idx+1:]) )
                # Inserts unpacked inputs into the list of inputs
                self.inputs[idx:idx+1] = ins

            elif lctn == 'OUTPUTS':
                key = (pack, val)
                idx = self.outputs.index(key)
                if mat_lnk is not None:
                    nb_ins = len(self.inputs)
                    nb_outs = len(outs)
                    # Inserts rows into the matrix for packed outputs
                    shape = (nb_outs, nb_ins)
                    vals = np.zeros(shape, dtype=np.int64)
                    vals += mat_res[idx,:][np.newaxis,:]
                    mat_res = np.vstack( (mat_res[0:idx,:], vals, mat_res[idx+1:,:]) )
                # Inserts unpacked outputs into the list of outputs
                self.outputs[idx:idx+1] = outs

        return mat_res


    '''
    LIMITS
    '''
    def _check_limit_ok(self, mode):
        len_in = len(self.inputs)
        len_out = len(self.outputs)
        max_card = max(len_in, len_out)
        return True if (max_card <= self.max_txos) else False
