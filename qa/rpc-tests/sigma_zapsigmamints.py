#!/usr/bin/env python3
import time
from decimal import *

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import *


#`zapsigmamints` conf setting test case

# Description: `zapsigmamints` configuration setting was added. What this does is clears the WalletDB of HD mints
#  (needed in case of deep re-org - https://en.bitcoin.it/wiki/Chain_Reorganization)
# 1. start wallet
# 2. mine blocks
# 3. mint some coins
# 4. spend a coin
# 5. restart with `zapsigmamints`
# 6. verify same mints present in listsigmamints
class SigmaZapSigmaMintsTest(BitcoinTestFramework):
    def __init__(self):
        super().__init__()
        self.num_nodes = 4
        self.setup_clean_chain = False

    def setup_nodes(self):
        # This test requires mocktime
        enable_mocktime()
        return start_nodes(self.num_nodes, self.options.tmpdir)

    def run_test(self):
        getcontext().prec = 6
        self.sync_all()

        sigma_denoms = [0.05, 0.1, 0.5, 1, 10, 25, 100]

        self.nodes[0].generate(401)

        self.nodes[0].mint(sum(sigma_denoms))

        self.nodes[0].generate(10)

        sigma_mints1 = self.nodes[0].listunspentsigmamints()
        assert len(sigma_mints1) > 1, 'Should be some sigma mints after mint, but was: {}' \
            .format(len(sigma_mints1))

        # stop nodes
        stop_nodes(self.nodes)

        self.nodes = start_nodes(1, self.options.tmpdir, "-zapsigmamints")
        self.sync_all()

        sigma_mints2 = self.nodes[0].listunspentsigmamints()

        assert len(sigma_mints2) == len(sigma_mints1), \
            'The amount of mints should be same after restart with zapsigmamints.'

        # Minting after restart with '-zapsigmamints'
        self.nodes[0].mint(sigma_denoms[0])

        self.nodes[0].generate(50)

        sigma_mints2 = self.nodes[0].listunspentsigmamints()

        # Mints count should pass even after restart with '-zapsigmamints'
        assert len(sigma_mints2) == len(sigma_mints1) + 1, \
            'After restart with zapsigmamints mint does not work.'

        # Check that we can generate blocks after
        self.nodes[0].generate(1)


if __name__ == '__main__':
    SigmaZapSigmaMintsTest().main()