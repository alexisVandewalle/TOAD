Retrieve events from the blockchain
===================================
The script **event_retriever.py** is a part of the client.
It periodically watch for events from the smart contract and save them in
the database.

Details of the algorithm
^^^^^^^^^^^^^^^^^^^^^^^^
When you launch this script, the first it does is to watch for the event
indicating that a group has been created. Once it has detected that a group has been
created, it moves to a new loop.
In this loop, it checks if a group public key has
been realeased. If it is the case, it saves this key in the database.
It checks if it is possible to compute the master public key, and saves it
in the database if it is possible.
It checks if a new file has been encrypted and saves the id of the file on ipfs and
the encryption parameters in the database.
It checks if a group member has published a share for some message, verifies it and
saves it in the database. 
