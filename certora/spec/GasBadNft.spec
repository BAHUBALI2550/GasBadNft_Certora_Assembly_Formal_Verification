/*
 * Verification of GasBadNft
 */

using GasBadNftMarketplace as gasBadMarketplace; 
using NftMock as nft;
using NftMarketplace as marketplace;

methods {
    function buyItem(address,uint256) external;
    function cancelListing(address,uint256) external;
    function listItem(address,uint256,uint256) external;
    function withdrawProceeds() external;
    function updateListing(address,uint256,uint256) external;

    function getListing(address nftAddress, uint256 tokenId) external returns(INftMarketplace.Listing) envfree;
    function getProceeds(address seller) external returns uint256 envfree;

    // use the nftMock.safeTransferFrom for all safeTransferFrom calls
    // we are assuming safeTransferFrom and onERC721Received are not having any reentrancy issues by assigning DISPATCHER(true)
    // however is this contract it may have reentrancy issue but we ignore it in testing otherwise certora will havoc these functions
    function _.safeTransferFrom(address,address,uint256) external => DISPATCHER(true);
    function _.onERC721Received(address,address,uint256,bytes) external => DISPATCHER(true);
}

ghost mathint listingUpdatesCount {
    init_state axiom listingUpdatesCount == 0;
    // initial state will be 0
    // require such to be true
    // axiom works like require
}
ghost mathint log4Count {
    init_state axiom log4Count == 0;
}

// hook Sstore s_listings[KEY address nftAddress][KEY uint256 tokenId].price uint256 price STORAGE{
//     listingUpdatesCount = listingUpdatesCount + 1;
// }

hook LOG4(uint offset, uint length, bytes32 t1, bytes32 t2, bytes32 t3, bytes32 t4) {
    log4Count = log4Count + 1;
}

// infact we should check if a event is emited whenever store variable is updated
// but this is an easy way to do this
invariant anytime_mapping_updated_emit_event()
    listingUpdatesCount <= log4Count;

rule calling_any_function_should_result_in_each_contract_having_the_same_state(method f, method f1, address listingAddr, uint256 tokenId, address seller){
    // going to call same functions on Nftmarketplace and GasBad
    // the getter functions of both should be same
    env e;
    calldataarg args;

    // They start in the same state
    require(gasBadMarketplace.getProceeds(e, seller) == marketplace.getProceeds(e, seller));
    require(gasBadMarketplace.getListing(e, listingAddr, tokenId).price == marketplace.getListing(e, listingAddr, tokenId).price);
    require(gasBadMarketplace.getListing(e, listingAddr, tokenId).seller == marketplace.getListing(e, listingAddr, tokenId).seller);

    // It's the same function on each
    require(f.selector == f1.selector);
    gasBadMarketplace.f(e, args);
    marketplace.f1(e, args);

    // They end in the same state
    assert(gasBadMarketplace.getListing(e, listingAddr, tokenId).price == marketplace.getListing(e, listingAddr, tokenId).price);
    assert(gasBadMarketplace.getListing(e, listingAddr, tokenId).seller == marketplace.getListing(e, listingAddr, tokenId).seller);
    assert(gasBadMarketplace.getProceeds(e, seller) == marketplace.getProceeds(e, seller));
}