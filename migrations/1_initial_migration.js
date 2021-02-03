const Migrations = artifacts.require("Migrations");
const TOAD = artifacts.require("TOAD");

module.exports = function (deployer) {
  deployer.deploy(Migrations);
  deployer.deploy(TOAD);
};
