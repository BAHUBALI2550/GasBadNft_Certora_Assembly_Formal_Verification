/*
 * Verification of NftMock
 */

methods {
    function totalSupply() external returns uint256 envfree;
    function mint() external;
    function balanceOf(address) external returns uint256 envfree;
}

// invariant totalSupplyNotnegative()
//     totalSupply() >= 0;

rule minting_mints_one_nft() {
    env e;
    address minter;

    require e.msg.value == 0;
    require e.msg.sender == minter;
    mathint balanceBefore = balanceOf(minter);

    currentContract.mint(e);

    assert to_mathint(balanceOf(minter)) == balanceBefore + 1, "Only 1 nft should be minted";
}

// rule sanity {
//     satisfy true;
// }