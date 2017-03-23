"""Abstract class for wrapping various providers of blockchain data."""
#from boltzmann.utils.transaction import Transaction

class BlockchainDataWrapper(object):
    """Retrieves data for specified transaction."""

    def get_tx(self, txid):
        """Returns a `Transaction` object for specified tx hash.

        Args:
            txid (str): The base58check-encoded transaction id.

        Returns: `Transaction`
        """
        raise NotImplementedError("This function should be implemented by"
                                  "subclasses.")
