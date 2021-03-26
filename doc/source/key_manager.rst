Generation of group key
=======================
The script **key_manager.py** automatically generates group secret key and
group public key when a file has been encrypted. To do that, it follows the
protocol described in the research paper which introduces TOAD protocol.

Details of the algorithm
^^^^^^^^^^^^^^^^^^^^^^^^
Firstly, the algorithm periodically checks if a group has been created. If it
is the case, it checks if the user who launches the algorithm is part of the
group thanks to his ethereum private key. Then two cases are possible: if the user
isn't part of the group, the algorithm ends raising an error indicating that
he is not a group member; in the other case the algorithm moves to the next step.
The next step is the protocol which allows to share a group secret key and a group
public key between all the member of the group. To do that, the algorithm:

  + generates an anonymous id and a temporary couple (private/public key) :math:`=(tsk_i, g^{tsk_i})`
  + chooses a secret :math:`s_i`
  + chooses a random polynomial :math:`f_i` such that :math:`f_i(0)=s_i`,
  + publishes the temporary public key
  + retrieves the temporary keys and anonymous ids of the other group member
  + evaluates the shares :math:`f_i(u_j)` where `u_j` is the anonymous id of the different group member
  + encrypts the shares with the key :math:`k_{ij} = tpk_j^{tsk_i}` and the algorithm salsa20
  + publishes the shares sorted by their corresponding :math:`u_j`
  + retrieves the shares of the other group members
  + decrypt the shares
  + computes its group secret key and group public key
  + publishes its group public key

Then the algorithm check if a new file has been encrypted and it generates
new group key pair for each new file with the following steps:

  + generates an anonymous id and a temporary couple (private/public key) :math:`=(tsk_i, g^{tsk_i})`
  + chooses a random polynomial :math:`f_i` such that :math:`f_i(0)=s_i`,
  + publishes the temporary public key
  + retrieves the temporary keys and anonymous ids of the other group member
  + evaluates the shares :math:`f_i(u_j)` where `u_j` is the anonymous id of the different group member
  + encrypts the shares with the key :math:`k_{ij} = tpk_j^{tsk_i}` and the algorithm salsa20
  + publishes the shares sorted by their corresponding :math:`u_j`
  + retrieves the shares of the other group members
  + decrypt the shares
  + computes its group secret key and group public key
  + publishes its group public key
