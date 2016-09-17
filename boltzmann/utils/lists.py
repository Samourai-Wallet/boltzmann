'''
Created on 20160917
Based on original works done in January 2015 for OXT
@author: LaurentMT
'''


'''
Util functions for lists
'''

def merge_sets(sets):
    '''
    Checks if sets from a list of sets share common elements
    and merge sets when common elements are detected
    Returns the list with merged sets
    Parameters:
        sets = list of sets
    '''
    tmp_sets = list(sets)
    merged = True
    while merged:
        merged = False
        res = []
        while tmp_sets:
            current, rest = tmp_sets[0], tmp_sets[1:]
            tmp_sets = []
            for x in rest:
                if x.isdisjoint(current):
                    tmp_sets.append(x)
                else:
                    merged = True
                    current |= x
            res.append(current)
        tmp_sets = res
    return tmp_sets
