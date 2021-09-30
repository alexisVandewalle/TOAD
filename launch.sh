#!/bin/bash
contract_address="0xd9CF9d6b7685e70064a4d6DCD724A248Faf39Ff5"
account="0x50365208718244dc38c6910d7b42379b135d5995caa1372fb79bc2e9d60f6704"
host="192.168.33.107"
port="8545"
source venv/bin/activate

ipfs daemon &

cd client/event_retriever
python event_retriever.py -c $contract_address -h $host -p $port &

cd ../key_manager
python key_manager.py -c $contract_address -s $account -h $host -p $port &

cd ..
export FLASK_APP=webapp
export FLASK_ENV=development
flask init-db
flask run
