# importing library
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


# part 1: building blockchain

class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.createBlock(proof=1, previous_hash='0')
        self.nodes = set()

    def createBlock(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions
                 }
        self.transactions = []
        self.chain.append(block)
        return block

    def getPreviousBlock(self):
        return self.chain[-1]

    def proofOfWork(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[0:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def isChainValid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[0:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    def addTransaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.getPreviousBlock()
        return previous_block['index'] + 1

    def addNode(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replaceChain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.isChainValid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False


# part 2: mining our blockchain

# a) creating the web app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# b) creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')

# c) creating the blockchain
blockchain = Blockchain()


# d) mining a new block


@app.route('/mine_block', methods=['GET'])
def mineBlock():
    previous_block = blockchain.getPreviousBlock()
    previous_proof = previous_block['proof']
    proof = blockchain.proofOfWork(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.addTransaction(sender=node_address, receiver='Gurbaaz', amount=1)
    block = blockchain.createBlock(proof, previous_hash)
    response = {'message': 'Yayyy!!! You just mined a block',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']
                }
    return jsonify(response), 200


# e) verify blockchain


@app.route('/is_valid', methods=['GET'])
def isValid():
    is_valid = blockchain.isChainValid(blockchain.chain)
    if is_valid:
        response = {'message': 'Yayy!!! Your Blockchain is valid.'}
    else:
        response = {'message': 'Ono, the Blockchain is not valid.'}

    return jsonify(response), 200


# f) get full blockchain

@app.route('/get_chain', methods=['GET'])
def getChain():
    response = {'chain': blockchain.chain, 'length': len(blockchain.chain)}
    return jsonify(response), 200


# g) Adding new transaction to the blockchain
@app.route('/add_transaction', methods=['POST'])
def addTransaction():
    json = request.get_json()
    transactions_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transactions_keys):
        return 'Missing information', 400
    index = blockchain.addTransaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to the Block {index}'}
    return jsonify(response), 201


# Part 3 Decentralizing Blockchain

# a) Connecting new nodes
@app.route('/connect_node', methods=['POST'])
def connectNode():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No node', 400
    for node in nodes:
        blockchain.addNode(node)
    response = {
        'message': 'All the nodes are now connected. The TimmyCoin Blockchain now contains the following nodes:',
        'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201


# b) Replacing chain with the longest chain
@app.route('/replace_chain', methods=['GET'])
def replaceChain():
    is_chain_replaced = blockchain.replaceChain()
    if is_chain_replaced:
        response = {'message': 'The chain is different therefore was replaced with the longest chain',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All Good !!! The chain is already the longest one',
                    'chain': blockchain.chain}
    return jsonify(response), 200


# running the app
app.run(host='0.0.0.0', port=5000)
