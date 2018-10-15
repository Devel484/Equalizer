"""
author: Devel484
"""


class Contract(object):

    def __init__(self, blockchain, version_hash):
        """
        Creates a contract with all versions
        :param blockchain: name of the blockchain i.e. NEO
        :param version_hash: hash of the blockchain
        """
        self.blockchain = blockchain
        self.version_hash = version_hash
        self.version = sorted(version_hash, reverse=True)

    def get_blockchain(self):
        """
        :return: blockchain name
        """
        return self.blockchain

    def get_latest_version(self):
        """
        :return: version of contract
        """
        return self.version[0]

    def get_latest_hash(self):
        """
        :return: latest contract hash
        """
        return self.version_hash[self.get_latest_version()]
