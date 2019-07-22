import hashlib

def sha256(strng):
    return hashlib.sha256(strng.encode()).hexdigest()

class ToyMerkleTree(object):

    def __init__(self,leaf,branch,root):
        #only 4 leaves {"0x1":str,"0x2":str,"0x3":str,"0x4":str}
        self.leaf = leaf
        #leaves to branch hash {"0x10x2":XX,"0x30x4":XX}
        self.branch = branch
        #hash of "0x10x2"&"0x30x4"
        self.root = root

    def make_branch_and_root(self):
        self.branch["0x10x2"] = sha256(self.leaf["0x1"]+self.leaf["0x2"])
        self.branch["0x30x4"] = sha256(self.leaf["0x3"]+self.leaf["0x4"])
        self.root = sha256(self.branch["0x10x2"]+self.branch["0x30x4"])

    def proof(self,root,address,value,proof_leaf_value,proof_branch_value):

        if address == "0x1":
            return sha256(sha256(value+proof_leaf_value)+proof_branch_value)==root
        if address == "0x2":
            return sha256(sha256(proof_leaf_value+value)+proof_branch_value)==root
        if address == "0x3":
            return sha256(proof_branch_value+sha256(value+proof_leaf_value))==root
        if address == "0x4":
            return sha256(proof_branch_value+sha256(proof_leaf_value+value))==root

if __name__ == "__main__":

    
    leaf_data = {"0x1":"100","0x2":"1000","0x3":"500","0x4":"166"}
    mt = ToyMerkleTree(leaf_data,{},"")
    mt.make_branch_and_root()
    
    br34 = mt.branch["0x30x4"]
    root = mt.root
    result = mt.proof(root,"0x2","1000","100",br34)
    print(result)
