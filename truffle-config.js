const PrivateKeyProvider = require("@truffle/hdwallet-provider");
const privateKey = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d";
const privateKeyProvider = new PrivateKeyProvider(privateKey, "http://192.168.33.107:8545");

module.exports = {
  // See <http://truffleframework.com/docs/advanced/configuration>
  // for more about customizing your Truffle configuration!
  networks: {
    besuWallet: {
      provider: privateKeyProvider,
      network_id: "*"
    },
  }
};

