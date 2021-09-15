#!/bin/bash
contract_address=""
account="0x8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63"
host="192.168.33.107"
port="8545"
source venv/bin/activate

truffle migrate --network=besuWallet
ipfs daemon --api /ip4/192.168.33.107/tcp/5001

cd client/event_retriever
python event_retriever.py -c $contract_address -h $host -p $port &

cd ../key_manager
python key_manager.py -c $contract_address -s $val -h $host -p $port &

cd ..
export FLASK_APP=webapp
export FLASK_ENV=development
flask init-db
flask run
