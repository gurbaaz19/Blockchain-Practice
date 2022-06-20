# importing library
import datetime
import hashlib
import json
from flask import Flask, jsonify

# building blockchain
class Blockchain:

    def __init__(self):
        self.chain = []
        self.createBlock(proof=1, previous_hash='0')

    def createBlock(self, proof, previous_hash):
        block = {'index': len(self.chain)+1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block
    
    def getPreviousBlock(self):
        return self.chain[-1]


# mining our blockchain
