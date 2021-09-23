#!/bin/bash
contract_address="0x5b1869D9A4C187F2EAa108f3062412ecf0526b24"
account="0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
host="192.168.33.107"
port="8545"
source venv/bin/activate

cd client/event_retriever
python event_retriever.py -c $contract_address -h $host -p $port &

cd ../key_manager
python key_manager.py -c $contract_address -s $account -h $host -p $port &

cd ..
export FLASK_APP=webapp
export FLASK_ENV=development
flask init-db
flask run
