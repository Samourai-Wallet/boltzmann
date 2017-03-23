"""Verifies that all providers of blockchain data are consistent with others."""
import unittest
try:
    from boltzmann.utils.bitcoind_rpc_wrapper import BitcoindRPCWrapper
    from boltzmann.utils.bci_wrapper import BlockchainInfoWrapper
except ImportError:
    import sys
    import os
    # Adds boltzmann directory into path
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../../")
    from boltzmann.utils.bitcoind_rpc_wrapper import BitcoindRPCWrapper
    from boltzmann.utils.bci_wrapper import BlockchainInfoWrapper


class CompareTest(unittest.TestCase):
    """Compare the results of various providers for given transaction IDs."""

    PROVIDERS = [BitcoindRPCWrapper, BlockchainInfoWrapper]

    #a list of transactions with expected data
    TEST_TXS = [
        {'height': 100001,
         'time': 1293624404,
         'txid': '8131ffb0a2c945ecaf9b9063e59558784f9c3a74741ce6ae2a18d0571dac15bb',
         'inputs': [{'n': 0,
                     'value': 5000000000,
                     'address': '1HYAekgNKqQiCadt3fnKdLQFFNLFHPPnCR',
                     'tx_idx': 239354,
                     'script': '4104cd31654088e472c60ab1c6ee7743deb186dce0b1ad5fc45691d37dad2620128e4b33c7c9c19ed01a5817e6e54c12fe1b83eafcb830440f23a2ce903cdb1df52fac'
                    },
                    {'n': 0,
                     'value': 5000000000,
                     'address': '16hwoJvz1xje8HBgoLZcxwo1CwE3cvkb17',
                     'tx_idx': 239356,
                     'script': '41041e1f1bdccf8cd5b9d3ffc0a14a36ad8a97663f14d16b94104d073abfc693d04178f263495cd6037aed097175297b39cfe5f5b9706fd425795bf7f61108145b53ac'
                    },
                    {'n': 0,
                     'value': 5000000000,
                     'address': '1KWGBfAsuBFzKQ7bhSJV5WbgVNvvQ5R1j2',
                     'tx_idx': 239322,
                     'script': '41043ea537ed214d2bcb07f56d2ecb047a4bd11d13fa160856f84e77e8d31ab2154cd2eb8cad37747b50b0b04d739186058d64212368202d1b41bc44fcb6decb90eaac'
                    },
                    {'n': 0,
                     'value': 5000000000,
                     'address': '15XgnazTwLj7sNPkbUo5vCSKBmR43X5vW4',
                     'tx_idx': 239205,
                     'script': '4104b2424b051a79a55b9f7970ceeecb25e81b876c53d9e46d6ee7e0ae656b94f8cf3a27a1b3f2465ac19409e2a08fb7d1f549adc70a5f90ff8418061688186064f4ac'
                    },
                    {'n': 0,
                     'value': 5001000000,
                     'address': '16HjHvF5umsgAzaX2ddosB81ttkrVHkvqo',
                     'tx_idx': 239162,
                     'script': '4104a7d578da4514a14b08d1e939924efaeacfde7d7d2897f2cef87248aaa4e3cd226f0660b9bf759448f9fb2f586f6027667b73d34a8114186265f9364193599c2cac'
                    }],
         'outputs': [{'n': 0,
                      'value': 25000000000,
                      'address': '15xif4SjXiFi3NDEsmMZCfTdE9jvvVQrjU',
                      'tx_idx': 240051,
                      'script': '76a914366a27645806e817a6cd40bc869bdad92fe5509188ac'
                     },
                     {'n': 1,
                      'value': 1000000,
                      'address': '1NkKLMgbSjXrT7oHagnGmYFhXAWXjJsKCj',
                      'tx_idx': 240051,
                      'script': '76a914ee8bd501094a7d5ca318da2506de35e1cb025ddc88ac'
                     }]
        },
        {'height': 299173,
         'time': 1399267359,
         'txid': '8e56317360a548e8ef28ec475878ef70d1371bee3526c017ac22ad61ae5740b8',
         'inputs': [{'n': 0,
                     'value': 10000000,
                     'address': '1FJNUgMPRyBx6ahPmsH6jiYZHDWBPEHfU7',
                     'tx_idx': 55795695,
                     'script': '76a9149cdac2b6a77e536f5f4ab6518fb078861f4dbf5188ac',
                    },
                    {'n': 1,
                     'value': 1380000,
                     'address': '1JDHTo412L9RCtuGbYw4MBeL1xn7ZTuzLH',
                     'tx_idx': 55462552,
                     'script': '76a914bcccdf22a567d2c30762c2c44edd3d4ff40e944c88ac'
                    }],
         'outputs': [{'n': 0,
                      'value': 100000,
                      'address': '1JR3x2xNfeFicqJcvzz1gkEhHEewJBb5Zb',
                      'tx_idx': 55819527,
                      'script': '76a914bf06953ec3c533d040929dc82eb4845ec0d8171088ac'
                     },
                     {'n': 1,
                      'value': 9850000,
                      'address': '18JNSFk8eRZcM8RdqLDSgCiipgnfAYsFef',
                      'tx_idx': 55819527,
                      'script': '76a9145011d8607971901c1135c2e8ae3074c472af4bf188ac'
                     },
                     {'n': 2,
                      'value': 100000,
                      'address': '1ALKUqxRb2MeFqomLCqeYwDZK6FvLNnP3H',
                      'tx_idx': 55819527,
                      'script': '76a91466607632dc9e3c0ed2e24fe3c54ea488408e99f588ac'
                     },
                     {'n': 3,
                      'value': 1270000,
                      'address': '1PA1eHufj8axDWEbYfPtL8HXfA66gTFsFc',
                      'tx_idx': 55819527,
                      'script': '76a914f3070c305b4bca72aa4b57bcbad05de5a692f16a88ac'
                     }
                    ]
        }]
    '''
        TODO:Both of these currently raise exception for BCI, so shouldnt work for RPC either
        { #genesis block coinbase tx
            'height': 0,
            'time': 1231006505,
            'txid': '4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b',
            'inputs': [{}], #TODO
            'outputs': [{}] #TODO
        },
        { #BIP30 duplicate tx, see:
          #https://github.com/kristovatlas/interesting-bitcoin-data
            'height': 91842, #also height 91812
            'time': 1289757588,
            'txid': 'd5d27987d2a3dfc724e359870c6644b40e497bdc0589a033220fe15429d88599',
            'inputs': [{}], #TODO
            'outputs': [{}] #TODO
        }
    '''

    def test(self):
        """Verify that fields are present and as expected for each data provider."""
        for test_idx, expected_tx in enumerate(self.TEST_TXS):
            for provider in self.PROVIDERS:
                prov = provider()
                print("Starting test # {0}".format(test_idx+1))
                txn = prov.get_tx(expected_tx['txid'])
                _assertEq(expected_tx['txid'], txn.txid, test_idx+1)
                _assertNoneOrEqual(txn.time, expected_tx['time'], test_idx+1)
                _assertEq(
                    len(expected_tx['inputs']), len(txn.inputs), test_idx+1)
                _assertEq(
                    len(expected_tx['outputs']), len(txn.outputs), test_idx+1)
                for idx, tx_in in enumerate(expected_tx['inputs']):
                    _assertEq(tx_in['n'], txn.inputs[idx].n, test_idx+1)
                    _assertEq(tx_in['value'], txn.inputs[idx].value, test_idx+1)
                    _assertEq(
                        tx_in['address'], txn.inputs[idx].address, test_idx+1)
                    _assertNoneOrEqual(
                        txn.inputs[idx].tx_idx, tx_in['tx_idx'], test_idx+1)
                for idx, tx_out in enumerate(expected_tx['outputs']):
                    _assertEq(tx_out['n'], txn.outputs[idx].n, test_idx+1)
                    _assertEq(
                        tx_out['value'], txn.outputs[idx].value, test_idx+1)
                    _assertEq(
                        tx_out['address'], txn.outputs[idx].address, test_idx+1)
                    _assertNoneOrEqual(
                        txn.outputs[idx].tx_idx, tx_out['tx_idx'], test_idx+1)

def _assertEq(a, b, test_num):
    assert a == b, "Test {0}: {1} != {2}".format(test_num, a, b)

def _assertNoneOrEqual(a, b, test_num):
    assert a is None or a == b, \
        "Test {0}: {1} != None && != {2}".format(test_num, a, b)

if __name__ == '__main__':
    unittest.main()
