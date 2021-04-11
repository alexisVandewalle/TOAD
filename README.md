# TOAD

This repository is an implementation of the protocol named TOAD (ThreshOld Anymous Decryption scheme).

## Interest of the protocol
The problem of security and privacy is a famous suject of debate in democracies. Indeed, in many democraties, one would like to improve security of people installing smart cameras in cities to find criminal quickly. However, when this type of product is installed, every people can be potentially observed which is a problem of privacy.

The idea behind our protocol is that each camera encrypts all the data it records. The secret key for decryption is made such that it is shared among several people in a group and nobody knows the secret key. If a group member wants to decrypt a specific record, he must collaborate with a sufficient number of group member to decrypt the record. In this way, the records are never available unless a specific number of group member decides to decrypt a record. The group members can be for instance elected people. Thus security and democracry are stronger while privacy is preserved.

## Installation
On linux you can try to run the script install.sh by running
```bash
  sudo bash install.sh
 ```
 It will execute the following step:
+ Create a python virtual environment and activate it
```bash
  python -m venv venv
  source venv/bin/activate (linux)
  .\venv\Scripts\Activate.ps1 (windows)
```
+ Install the python dependencies
```bash
  pip install -r requirements.txt
 ```
 + Install truffle and ganache-cli
 ```bash
  npm install truffle
  npm install ganache-cli
 ```
 + Install ipfs
 ```bash
 choco install ipfs (windows)
 snap install ipfs (linux)
 ```
 + Init ipfs
 ```bash
 ipfs init
 ```

 ## Running the application
 The easiest way to run the application is to run the script launch.sh
 with this command:
 ```bash
 bash launch.sh <number of clients>
 ```
 This script does the following step:
  + activate python virtual environnement
  + run ganache-cli with deterministic key and id with 20 accounts
  + compile and deploy the contract TOAD.sol
  + launch the script event_retriever.py
  + launch key_manager.py (number of clients) times
  + run the web application to encrypt and decrypt files
