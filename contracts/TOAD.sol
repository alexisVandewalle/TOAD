pragma solidity >=0.5.0;
pragma experimental ABIEncoderV2;

contract TOAD{
    ///private variables
    EncryptedAccount[] private encrypted_public_account;

    /// public variables
    bool public has_been_used = false;
    bool public is_mpk_available = false;
    uint public N;
    uint public t;
    address public public_account;
    uint public round;
    uint public nb_group_key = 0;


    GroupKeyWithId[] public gpk_list;

    ///structures
    struct EncryptedAccount{
        bytes e_sk;
        bytes tag;
        bytes nonce;
    }

    struct GroupKeyWithId{
        uint anonymousId;
        uint256[2] gpk;
    }

    ///events
    event PublicKey(uint256[2] public_key, uint anonymous_id, uint round);
    event Share(bytes[] shares, uint round);
    event GroupKey(uint256[2] gpk, uint anonymous_id, uint round);
    event MasterGroupKeyAvailable();
    event ShareForDec(address sender, uint id, uint256[4] share, uint256[2] proof);
    event NewMessage(address sender, uint round, bytes file_hash, uint256[4] c1, uint256[4] c2);
    event GenerateNewKeys(uint round);
    event GroupCreation(address creator);

    function groupCreation(
        EncryptedAccount[] memory _group,
        uint _threshold
        ) public {

        require(!has_been_used,'group already created');
        has_been_used = true;

        N = _group.length;
        require(_threshold < N,'threshold must satisfy threshold<N');
        t = _threshold;
        public_account = msg.sender;
        round = 0;

        for(uint i=0; i<N;i++){
            encrypted_public_account.push(_group[i]);
        }

        emit GroupCreation(msg.sender);
    }

    function get_encrypted_public_account(uint i) public view returns (bytes[3] memory){
        require(i<N);
        return [encrypted_public_account[i].e_sk,
                encrypted_public_account[i].tag,
                encrypted_public_account[i].nonce];
    }

    function publish_pk(uint256[2] memory _public_key, uint _anonymous_id,uint _round) public{
        require(msg.sender == public_account, 'only user who have access to the public account can call this function');
        emit PublicKey(_public_key, _anonymous_id, _round);
    }

    function publish_share(bytes[] memory _shares, uint _round) public{
        require(msg.sender == public_account, 'only user who have access to the public account can call this function');
        emit Share(_shares, _round);
    }

    function register_group_key(uint256[2] memory _gpk, uint _anonymous_id, uint _round)public{
        require(msg.sender == public_account,'only user who have access to the public account can call this function');

        emit GroupKey(_gpk, _anonymous_id, _round);

        if(_round == 0){
            nb_group_key +=1;
            gpk_list.push(GroupKeyWithId(_anonymous_id, _gpk));
            if(nb_group_key == t +1){
                is_mpk_available = true;
                emit MasterGroupKeyAvailable();
            }
        }
    }

    function get_group_keys()public view returns(GroupKeyWithId[] memory){
        return gpk_list;
    }

    function send_msg(bytes memory file_hash, uint256[4] memory c1, uint256[4] memory c2) public{
        require(is_mpk_available, 'master key is not available');
        emit NewMessage(msg.sender,round, file_hash, c1, c2);
        if (round>0){
            emit GenerateNewKeys(round);
        }
        round = round + 1;
    }

    function share_for_dec(uint _round, uint256[4] memory _share, uint256[2] memory _proof) public{
        require(is_mpk_available, 'no message available');
        emit ShareForDec(msg.sender, _round, _share, _proof);
    }

}
