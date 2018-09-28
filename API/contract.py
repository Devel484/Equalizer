

class Contract(object):

    def __init__(self, chain, version_hash):
        self.chain = chain
        self.version_hash = version_hash
        self.version = sorted(version_hash, reverse=True)

    def get_chain(self):
        return self.chain

    def get_latest_version(self):
        return self.version[0]

    def get_latest_hash(self):
        return self.version_hash[self.get_latest_version()]
