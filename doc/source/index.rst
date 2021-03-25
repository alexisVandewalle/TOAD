.. TOAD documentation master file, created by
   sphinx-quickstart on Thu Mar 25 16:11:31 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to TOAD's documentation!
================================
This project is an implementation of TOAD protocol. This protocol is a distributed
encryption and decryption protocol which is described in this `paper`_.

General description
===================
The implementation includes two parts: a client and an ethereum smart contract
located in the blockchain. The client follow the protocol define in the paper and
interacts with the blockchain when it wants to publish message or receive message.
Thus the blockchain acts as a secure communication layer between the differents
clients who take part in the protocol.

Description of the client
^^^^^^^^^^^^^^^^^^^^^^^^^
The client is the central part of the implementation. It can be divised in three
different part:

  + a code which retrieves the event emited by the blockchain
  + a code which manages the generation of key
  + an interactive web application allowing to encrypt and decrypt files

Each part interacts with a same database where it saves or retrieves informations
about the protocol.

Description of the contract
^^^^^^^^^^^^^^^^^^^^^^^^^^^



.. toctree::
   :maxdepth: 2
   :caption: Contents:

   event_retriever
   key_manager
   encrypt_decrypt



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
