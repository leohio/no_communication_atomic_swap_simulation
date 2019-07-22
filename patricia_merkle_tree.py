def _verify(expected_root, key, proof, key_index, proof_index, expected_value):
    ''' Iterate the proof following the key.
        Return True if the value at the leaf is equal to the expected value.
        @param expected_root is the expected root of the current proof node.
        @param key is the key for which we are proving the value.
        @param proof is the proof the key nibbles as path.
        @param key_index keeps track of the index while stepping through
            the key nibbles.
        @param proof_index keeps track of the index while stepping through
            the proof nodes.
        @param expected_value is the key's value expected to be stored in
            the last node (leaf node) of the proof.
    '''
    node = proof[proof_index]
    dec = rlp.decode(node)
    
    if key_index == 0:
        # trie root is always a hash
        assert keccak(node) == expected_root
    elif len(node) < 32:
        # if rlp < 32 bytes, then it is not hashed
        assert dec == expected_root
    else:
        assert keccak(node) == expected_root
    
    if len(dec) == 17:
        # branch node
        if key_index >= len(key):
            if dec[-1] == expected_value:
                # value stored in the branch
                return True
        else:
            new_expected_root = dec[nibble_to_number[key[key_index]]]
            if new_expected_root != b'':
                return _verify(new_expected_root, key, proof, key_index + 1, proof_index + 1,
                               expected_value)
    elif len(dec) == 2:
        # leaf or extension node
        # get prefix and optional nibble from the first byte
        (prefix, nibble) = dec[0][:1].hex()
        if prefix == '2':
            # even leaf node
            key_end = dec[0][1:].hex()
            if key_end == key[key_index:] and expected_value == dec[1]:
                return True
        elif prefix == '3':
            # odd leaf node
            key_end = nibble + dec[0][1:].hex()
            if key_end == key[key_index:] and expected_value == dec[1]:
                return True
        elif prefix == '0':
            # even extension node
            shared_nibbles = dec[0][1:].hex()
            extension_length = len(shared_nibbles)
            if shared_nibbles == key[key_index:key_index + extension_length]:
                new_expected_root = dec[1]
                return _verify(new_expected_root, key, proof,
                               key_index + extension_length, proof_index + 1,
                               expected_value)
        elif prefix == '1':
            # odd extension node
            shared_nibbles = nibble + dec[0][1:].hex()
            extension_length = len(shared_nibbles)
            if shared_nibbles == key[key_index:key_index + extension_length]:
                new_expected_root = dec[1]
                return _verify(new_expected_root, key, proof,
                               key_index + extension_length, proof_index + 1,
                               expected_value)
        else:
            # This should not be reached if the proof has the correct format
            assert False
    return True if expected_value == b'' else False
