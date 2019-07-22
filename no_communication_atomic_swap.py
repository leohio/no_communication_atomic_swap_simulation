from toy_merkle_tree import ToyMerkleTree
from toy_merkle_tree import sha256
from copy import deepcopy
import time


class IdealTx(object):

    def __init__(self,update_address,update_data,print_text):

        self.update_address = update_address
        self.update_data = update_data
        self.print_text = print_text

    #EVM is omitted in this simulation
    def exe(self,merkle):
        merkle.leaf[self.update_address] = self.update_data
        print(self.print_text)



class IdealPoSBlock(object):

    def __init__(self,block_number,previous_merkle,txs,voters,previous_blockhash):
        self.block_number = block_number

        mpt = deepcopy(previous_merkle)
        for tx in txs:
            tx.exe(mpt)

        mpt.make_branch_and_root()
        self.merkle_patricia_tree = mpt
        self.world_state = mpt.root

        self.block_hash = sha256(previous_blockhash)
        #who voted and signed to the world state
        self.voters = voters



class IdealPoSChain(object):

    def __init__(self,blocks):
        self.blocks = blocks



class IdealPoSValidator(object):

    def __init__(self,address):
        self.address = address
   
    #double vote is banned by slasher
    def vote_to_block(self,block):
        if self.address not in block.voters:
            block.voters.append(self.address)



class AtomicSwapUser():

    #self.chain is the chain on which Alice sets the atomic swap contract
    #self.another_chain is the chain Bob pays Alice
    def __init__(self,address,chain,another_chain):
        self.address = address
        self.chain = chain    
        self.another_chain = another_chain

    def set_tx_contract_on_chain_as_alice(self,pay_to,alice_address,expected_another_chain_balance,expected_voters,block_hash_now):
        return {
            "pay_to":pay_to,
            # information below is about another chain
            "address_on_another_chain": alice_address,
            "expected_another_chain_balance":expected_another_chain_balance,
            "expected_voters":expected_voters,
            "block_hash":block_hash_now
        }
        
    def execute_atomicswap_contract_as_bob(self,contract,merkle_proof,voters):

        #contract is made at set_tx_contract_on_chain_as_alice
        current_block_on_another_chain = self.another_chain.blocks[-1]
        current_block_hash_on_another_chain = self.another_chain.blocks[-1].block_hash
        address = contract["pay_to"]
        balance = contract["expected_another_chain_balance"]
        merkle = current_block_on_another_chain.merkle_patricia_tree
        
        #these check1~3 below are on EVM if a real implemenation

        #proving the block of when the contract was set contract["block_hash"] is included in another_chain's head. this time is only 1-conf.
        check1 = (sha256(contract["block_hash"])==current_block_hash_on_another_chain)
        print("block_hash relation between Alice's contract and Bob's proof is proven")

        #prove the balance(state) change of another_chain on chain       
        check2 = merkle.proof(**merkle_proof)
        print("World State is proven to have a leaf that Alice's balance 150ETH2")
        #in real implementation, there's need of checking signatures by voters to a merkle_root (or block_hash which include merkle root) 
        check3 = set(current_block_on_another_chain.voters).issubset(set(voters))
        print("Voters' signs on world state is proven")
        
        if check1 and check2 and check3:
            alice_address_on_chain = "0x1"
            tx0 = IdealTx(alice_address_on_chain,"50","")
            tx = IdealTx(address,"60","Atomic Swap Done!! Alice paid Bob 50ETH")
            tx.exe(merkle)
        






##########################################################################
##########      this is the simulation in __main__             ###########
##########################################################################
            
def no_communication_atomic_swap_simulation():

    #####PREPARE#######
    chain = IdealPoSChain([])         
    another_chain = IdealPoSChain([])
    Alice = AtomicSwapUser("0x1",chain,another_chain)
    Bob = AtomicSwapUser("0x2",chain,another_chain)
    
    empty_storage1 = ToyMerkleTree({"0x1":"0","0x2":"0","0x3":"1000","0x4":"1000"},{},"")
    empty_storage2 = ToyMerkleTree({"0x1":"0","0x2":"0","0x3":"1000","0x4":"1000"},{},"")

    print("Alice's address is 0x1")
    print("Bob's address is 0x2")
    print("addresses of validators(rich-1 and rich-2) are 0x3 and 0x4")

    validator1_on_chain = IdealPoSValidator("0x3")
    validator2_on_chain = IdealPoSValidator("0x4")
    validator1_on_another_chain = IdealPoSValidator("0x3")
    validator2_on_another_chain = IdealPoSValidator("0x4")

    ###### BLOCK_NUMBER = 0 #########
    blank()
    print("Fist, we will mine 2 blocks on  'chain' and 'another_chain'")
    print("0: Generating genesis blocks of chain and another_chain")

    chain_genesis_block = IdealPoSBlock(0,empty_storage1,[],[],"chain")
    another_chain_genesis_block = IdealPoSBlock(0,empty_storage1,[],[],"another_chain")
    
    validator1_on_chain.vote_to_block(chain_genesis_block)
    validator2_on_chain.vote_to_block(chain_genesis_block)
    chain.blocks.append(chain_genesis_block)

    validator1_on_another_chain.vote_to_block(another_chain_genesis_block)
    validator2_on_another_chain.vote_to_block(another_chain_genesis_block)
    another_chain.blocks.append(another_chain_genesis_block)
    print("0: chains are updated block_number=0")

    ###### BLOCK_NUMBER = 1 #########
    blank()

    print("1: make txs to update storages and merkle tree on block_number=1")

    tx_0_1 = IdealTx("0x1","100","Alice(0x1) gets 100ETH on chain")
    tx_0_2 = IdealTx("0x2","10","Bob(0x2) gets 10ETH on chain")
    block1_on_chain = IdealPoSBlock(1,chain_genesis_block.merkle_patricia_tree,[tx_0_1,tx_0_2],[],chain_genesis_block.block_hash)
    validator1_on_chain.vote_to_block(block1_on_chain)
    validator2_on_chain.vote_to_block(block1_on_chain)

    chain.blocks.append(block1_on_chain)
    print("block_number=1 is mined and voted on 'chain'")
    
    tx_1_1 = IdealTx("0x1","50","Alice(0x1) gets 50ETH2 on another_chain")
    tx_1_2 = IdealTx("0x2","500","Bob(0x2) gets 500ETH2 on another_chain")
    tx_1_3 = IdealTx("0x3","1300","rich1(0x3) gets 1000ETH2 on another_chain")
    tx_1_4 = IdealTx("0x4","1300","rich2(0x4) gets 1000ETH2 on another_chain")

    block1_on_another_chain = IdealPoSBlock(1,another_chain_genesis_block.merkle_patricia_tree,[tx_1_1,tx_1_2,tx_1_3,tx_1_4],[],another_chain_genesis_block.block_hash)
    validator1_on_chain.vote_to_block(another_chain_genesis_block)
    validator2_on_chain.vote_to_block(another_chain_genesis_block)

    another_chain.blocks.append(block1_on_another_chain)
    print("block_number=1 is mined and voted on 'another_chain'")

    ########## ATOMIC SWAP STARTS ###########
    ###### BLOCK_NUMBER = 2 #########
    blank()


    print("Alice will set Atomic Swap Contract")
    atomicswap_contract = Alice.set_tx_contract_on_chain_as_alice("0x2","0x1","150",["0x3","0x4"],block1_on_another_chain.block_hash)

    
    block2_on_chain = IdealPoSBlock(2,block1_on_chain.merkle_patricia_tree,[],["0x3","0x4"],block1_on_chain.block_hash)

    print("Alice sets conditions that if Alice's balance get 150ETH2 on another chain, Alice will automatically pay Bob 50 ETH on chain")

    print("==block_number=2 is mined on chain==")
    print("Then Bob will pay 50 ETH2 on another chain")
    tx_1_5 = IdealTx("0x1","150","Bob did")
    block2_on_another_chain = IdealPoSBlock(2,block1_on_another_chain.merkle_patricia_tree,[tx_1_5],["0x3","0x4"],block1_on_another_chain.block_hash)
    
   
    chain.blocks.append(block2_on_chain)
    another_chain.blocks.append(block2_on_another_chain)
 
    ########## Bob completes Atomic Swap ###########
    ###### BLOCK_NUMBER = 3 #########
    blank()
    print("Bob will complete Atomic Swap by submitting the merkle proof which prove the balance of Alice on another chain.")
    blank()


    mt = block2_on_another_chain.merkle_patricia_tree
    print("the proof is ")
    merkle_proof = {
        "root":mt.root,
        "address":"0x1",
        "value":"150",
        "proof_leaf_value":mt.leaf["0x2"],
        "proof_branch_value":mt.branch["0x30x4"]
    } 
    print(merkle_proof)
    blank()
    Bob.execute_atomicswap_contract_as_bob(
        atomicswap_contract,
        merkle_proof,
        ["0x3","0x4"]
    )

def blank():
    time.sleep(4)
    print("")
    print("")
    print("=========================")
    print("")
    
if __name__ == "__main__":
    no_communication_atomic_swap_simulation() 
