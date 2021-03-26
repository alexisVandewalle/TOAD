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

Installation
============
On linux you can try to run the script install.sh by running

.. code-block:: bash

  sudo bash install.sh


It will execute the following step:

+ Create a python virtual environment and activate it

.. code-block:: bash

  python -m venv venv
  source venv/bin/activate (linux)
  .\venv\Scripts\Activate.ps1 (windows)


+ Install the python dependencies

.. code-block:: bash

  pip install -r requierements.txt


+ Install truffle and ganache-cli

.. code-block:: bash

  npm install truffle
  npm install ganache-cli


+ Install ipfs

.. code-block:: bash

  choco install ipfs (windows)
  snap install ipfs (linux)

+ Init ipfs

.. code-block:: bash

  ipfs init


Running the application
=======================
The easiest way to run the application is to run the script launch.sh
with this command:

.. code-block:: bash

  bash launch.sh <number of clients>

This script does the following step:

  + activate python virtual environnement
  + run ganache-cli with deterministic key and id with 20 accounts
  + compile and deploy the contract TOAD.sol
  + launch the script event_retriever.py
  + launch key_manager.py (number of clients) times
  + run the web application to encrypt and decrypt files



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
