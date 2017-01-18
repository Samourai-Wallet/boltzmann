# Boltzmann

A python script computing the entropy of Bitcoin transactions and the linkability of their inputs and outputs.

Initially developed for the OXT platform. 

Certainly, the worst implementation in the world but with a nice property: it exists :)


More information at:

- Bitcoin Transactions & Privacy (part 1) : https://gist.github.com/LaurentMT/e758767ca4038ac40aaf

- Bitcoin Transactions & Privacy (part 2) : https://gist.github.com/LaurentMT/d361bca6dc52868573a2

- Bitcoin Transactions & Privacy (part 3) : https://gist.github.com/LaurentMT/e8644d5bc903f02613c6



## Python versions

Python 3.3.3


## Dependencies

- sortedcontainers
- numpy


## Installation


Manual installation
```
Gets the library from Github : https://github.com/LaurentMT/boltzmann/archive/master.zip
Unzips the archive in a temp directory
python setup.py install
```



## Usage

python ludwig.py [--duration=600] [--maxnbtxos=12] [--cjmaxfeeratio=0] [--options=PRECHECK,LINKABILITY,MERGE_FEES,MERGE_INPUTS,MERGE_OUTPUTS] [--txids=8e56317360a548e8ef28ec475878ef70d1371bee3526c017ac22ad61ae5740b8,812bee538bd24d03af7876a77c989b2c236c063a5803c720769fc55222d36b47,...]

[-t OR --txids] = List of txids to be processed.

[-d OR --duration] = Maximum number of seconds allocated to the processing of a single transaction. 
                     Default value is 600 seconds.

[-x OR --maxnbtxos] = Maximum number of inputs or ouputs. 
                      Transactions with more than maxnbtxos inputs or outputs are not processed. 
                      Default value is 12.    

[-r OR --cjmaxfeeratio] = Max intrafees paid by the taker of a coinjoined transaction. 
                          Expressed as a percentage of the coinjoined amount.

[-o OR --options] = Options to be applied during processing. 
                    Default value is PRECHECK, LINKABILITY, MERGE_INPUTS.
                    Available options are :
                    
- PRECHECK = Checks if deterministic links exist without processing the entropy of the transaction. Similar to Coinjoin Sudoku by K.Atlas.
                      
- LINKABILITY = Computes the entropy of the transaction and the txos linkability matrix.
                      
- MERGE_INPUTS = Merges inputs "controlled" by a same address. Speeds up computations.
                      
- MERGE_OUTPUTS = Merges outputs "controlled" by a same address. Speeds up computations but this option is not recommended.
                      
- MERGE_FEES = Processes fees as an additional output paid by a single participant. May speed up computations.


## Author
Twitter: @LaurentMT


## Contributing

Help us to make Boltzmann better !

Many improvements are needed:
 - smarter heuristics to manage intra fees paid/received by participants to coinjoin markets (e.g. joinmarket, ...)
 - optimization of the algorithm (parallelization, memoization, ...)
 - ...

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request
