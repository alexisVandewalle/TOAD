pragma solidity >=0.5.0;
pragma experimental ABIEncoderV2;

contract TOAD{
    ///private variables

    /// public variables
    bool public has_been_used = false;
    uint public N;
    uint public t;

    ///structures
    struct EncryptedAccount{
        uint256 e_tag;
        uint256 e_sk;
        uint256 e_pk;
    }

    event GroupCreation(EncryptedAccount[] group, uint threshold, string label);

    function groupCreation(
        EncryptedAccount[] memory _group, 
        uint _threshold, 
        string memory _label
        ) public {
        
        require(!has_been_used);
        has_been_used = true;

        N = _group.length;
        require(_threshold < N);
        t = _threshold;

        emit GroupCreation(_group, _threshold, _label);
    }
}