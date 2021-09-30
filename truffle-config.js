const PrivateKeyProvider = require("@truffle/hdwallet-provider");
const privateKey = "0x50365208718244dc38c6910d7b42379b135d5995caa1372fb79bc2e9d60f6704";
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

