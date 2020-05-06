from hashlib import sha256
import requests
import json
import time
import threading

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    difficulty = 4

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.lock = threading.Lock()

    @classmethod
    def proof_valid(cls, block, block_hash):
        return (block_hash.startswith('0' * Blockchain.difficulty) and block_hash == block.compute_hash())

    @classmethod
    def chain_valid(cls, chain):
        result = True
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            delattr(block, "hash")

            if not cls.proof_valid(block, block_hash) or previous_hash != block.previous_hash:
                result = False
                break

            block.hash = block_hash
            previous_hash = block_hash

        return result

    @staticmethod
    def proof_of_work(block):
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    @property
    def last_block(self):
        return self.chain[-1]

    def __getBlockChain__(self):
        self.lock.acquire()
        try:
            arr = self.chain
            print('Acquired lock for capturing chain',arr,self.chain)

        finally:
            print('Released lock for capturing chain')
            self.lock.release()
            return arr

    def generate_block_zero(self):
        genesis_block = Block(0, [], 0, "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)


    def add_block(self, block, proof):
        
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if Blockchain.proof_valid(block, proof) == False:
            return False

        block.hash = proof
        self.chain.append(block)
        return True


    def add_new_transaction(self, transaction):
        self.lock.acquire()
        try:
            print('Acquired lock for new transaction')
            self.unconfirmed_transactions.append(transaction)
        finally:
            print('Released lock for new transaction')
            self.lock.release()


    def mine(self):
        self.lock.acquire()
        try:
            print('Acquired a lock for mining')
            if not self.unconfirmed_transactions:
                return False

            last_block = self.last_block

            new_block = Block(index = last_block.index + 1, transactions = self.unconfirmed_transactions, timestamp = time.time(), previous_hash = last_block.hash)

            proof = self.proof_of_work(new_block)
            self.add_block(new_block, proof)

            self.unconfirmed_transactions = []

        finally:
            print('Released lock for mining')
            self.lock.release()
            return True