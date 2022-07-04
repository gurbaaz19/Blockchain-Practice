// TimmyCoin ICO

// Compiler Version
pragma solidity ^0.4.11;

contract timmycoin_ico {
    // Introducing total number of TimmyCoins to be circulated
    uint public max_timmycoins = 1000000;

    // Introducing the USD - TimmyCoin conversion rate
    uint public usd_to_timmycoins = 1000;

    // Introducing the Timmy Coins bought by investors
    uint public total_timmycoins_bought = 0;

    // Mapping from the investor address to its equity in TimmyCoins and USD
    mapping(address => uint) equity_timmycoins;
    mapping(address => uint) equity_usd;

    // Checking if an investor can buy Timmycoins
    modifier can_buy_timmycoins(uint usd_invested) {
        require(usd_invested * usd_to_timmycoins + total_timmycoins_bought <= max_timmycoins);
        _;
    }

    // Getting the equity in Timmycoins of an investor
    function equity_in_timmycoins(address investor) external constant returns (uint) {
        return equity_timmycoins[investor];
    }

    // Getting the equity in USD of an investor
    function equity_in_usd(address investor) external constant returns (uint) {
        return equity_usd[investor];
    }

    // Buying Timmycoins
    function buy_timmycoins(address investor, uint usd_invested) external
    can_buy_timmycoins(usd_invested) {
        uint timmycoins_bought = usd_invested * usd_to_timmycoins;
        equity_timmycoins[investor] += timmycoins_bought;
        equity_usd[investor] += equity_timmycoins[investor] / usd_to_timmycoins;
        total_timmycoins_bought += timmycoins_bought;
    }

    // Selling Timmycoins
    function sell_timmycoins(address investor, uint timmycoins_to_sell) external {
        equity_timmycoins[investor] -= timmycoins_to_sell;
        equity_usd[investor] += equity_timmycoins[investor] / usd_to_timmycoins;
        total_timmycoins_bought -= timmycoins_to_sell;
    }
}
