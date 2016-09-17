# Boltzmann

A python script computing the entropy of Bitcoin transactions and the linkability of their inputs and outputs.

Initially developed for the OXT platform. 
Certainly, the dumbest implementation in the world but with a nice property: it exists :)


More information at:

- Bitcoin Transactions & Privacy (part 1) : https://gist.github.com/LaurentMT/e758767ca4038ac40aaf

- Bitcoin Transactions & Privacy (part 2) : https://gist.github.com/LaurentMT/d361bca6dc52868573a2

- Bitcoin Transactions & Privacy (part 3) : https://gist.github.com/LaurentMT/e8644d5bc903f02613c6



## Python versions

Unit tests passed for Python 3.3.3


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

python ludwig.py [--duration=600] [--options=PRECHECK,LINKABILITY,MERGE_FEES] [--txids=8e56317360a548e8ef28ec475878ef70d1371bee3526c017ac22ad61ae5740b8,812bee538bd24d03af7876a77c989b2c236c063a5803c720769fc55222d36b47,...]

## Author
Twitter: @LaurentMT


## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request
