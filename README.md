# TOAD

This repository is an implementation of the protocol named TOAD (ThreshOld Anymous Decryption scheme).

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
  pip install -r requierements.txt
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
