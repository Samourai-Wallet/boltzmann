# Boltzmann

A python script computing the entropy of Bitcoin transactions and the linkability of their inputs and outputs.

For a description of the metrics :

- Bitcoin Transactions & Privacy (part 1) : https://gist.github.com/LaurentMT/e758767ca4038ac40aaf

- Bitcoin Transactions & Privacy (part 2) : https://gist.github.com/LaurentMT/d361bca6dc52868573a2

- Bitcoin Transactions & Privacy (part 3) : https://gist.github.com/LaurentMT/e8644d5bc903f02613c6



## Python versions

Python 3.3.3


## Dependencies

- sortedcontainers
- numpy
- python-bitcoinrpc
- mpmath
- sympy


## Installation


Manual installation
```
Gets the library from Github : https://github.com/LaurentMT/boltzmann/archive/master.zip
Unzips the archive in a temp directory
python setup.py install
```



## Usage

python ludwig.py [--rpc] [--duration=600] [--maxnbtxos=12] [--cjmaxfeeratio=0] [--options=PRECHECK,LINKABILITY,MERGE_FEES,MERGE_INPUTS,MERGE_OUTPUTS] [--txids=8e56317360a548e8ef28ec475878ef70d1371bee3526c017ac22ad61ae5740b8,812bee538bd24d03af7876a77c989b2c236c063a5803c720769fc55222d36b47,...]

[-t OR --txids] = List of txids to be processed.

[-p OR --rpc] = Use bitcoind's RPC interface as source of blockchain data

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


## Troubleshooting

This project requires python 3. If your default `python` points to python 2, substitute `python3` for all instructions in this README.

## Data Sources

You can use the remote Blockchain.info API for blockchain data (default), bitcoind's local RPC interface using the `--rpc` command line option, or write your own wrapper.

In order to use bitcoind's RPC interface, you must set these environment variables:
* BOLTZMANN_RPC_USERNAME
* BOLTZMANN_RPC_PASSWORD
* BOLTZMANN_RPC_HOST
* BOLTZMANN_RPC_PORT

Ex. `$ export BOLTZMANN_RPC_USERNAME=myusername`

You will also need to enable full indexing for bitcoind. This consumes more storage space. See this sample excerpt of a `bitcoin.cfg` file:
```
# You must set rpcuser and rpcpassword to secure the JSON-RPC api
rpcuser=myusername
rpcpassword=mysecretpassword_REPLACE_ME
rpcport=8332

#Maintain a full transaction index, used by the getrawtransaction rpc call (default: 0)
txindex=1
```

## Contributors
@LaurentMT 
@kristovatlas


## Contributing

Many improvements are needed:
 - smarter heuristics to manage intra fees paid/received by participants to coinjoin markets (e.g. joinmarket, ...)
 - optimization of the algorithm (parallelization, memoization, ...)
 - ...

Help us to make Boltzmann better !

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request

Tip: Don't forget to run `python setup.py clean && python setup.py build && python setup.py install` after modifying source files.
