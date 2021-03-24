#!/bin/bash
contract_address="0x5b1869D9A4C187F2EAa108f3062412ecf0526b24"
declare -a account=("0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d" "0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1" "0x6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c" "0x646f1ce2fdad0e6deeeb5c7e8e5543bdde65e86029e2fd9fc169899c440a7913")
source venv/bin/activate

npx ganache-cli -d &
npx truffle migrate
ipfs --offline daemon &

cd client/event_retriever
python event_retriever.py -c $contract_address &

cd ../key_manager
for val in "${account[@]}"; do
  sleep 1
  python key_manager.py -c $contract_address -s $val &
done

cd ..
export FLASK_APP=webapp
export FLASK_ENV=development
flask init-db
flask run
