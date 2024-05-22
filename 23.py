
// SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import "hardhat/console.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract NFTMarketPlace is ERC721URIStorage {
    uint256 private _tokenIds;
    address payable owner;
    uint256 public listPrice = 0.01 ether;
    uint256[] public allListedTokens;
    
    // Address to withdraw listing fees
    address public feeCollector;

    // Event for fee withdrawal
    event ListingFeeWithdrawn(address indexed collector, uint256 amount);

    struct ListedToken {
        uint256 tokenId;
        address payable owner;
        address payable seller;
        uint256 price;
        bool currentlyListed;
    }

    struct Bid {
        address bidder;
        uint256 amount;
        uint256 timestamp;
    }

    struct AuctionItem {
        uint256 tokenId;
        address seller;
        uint256 startPrice;
        uint256 highestBid;
        address payable highestBidder;
        uint256 auctionEndTime;
        bool active;
        Bid[] bids;
    }
    event TokenListedSuccess(
        uint256 indexed tokenId,
        address owner,
        address seller,
        uint256 price,
        bool currentlyListed
    );

    event AuctionStarted(
        uint256 indexed tokenId,
        address seller,
        uint256 startPrice,
        uint256 auctionEndTime
    );

    event BidPlaced(
        uint256 indexed tokenId,
        address bidder,
        uint256 amount
    );

    event AuctionEnded(
        uint256 indexed tokenId,
        address indexed seller,
        address indexed winner,
        uint256 amount
    );

    mapping(uint256 => ListedToken) private idToListedToken;
    mapping(address => uint256[]) private unlistedTokens;
    mapping(address => uint256[]) private listedTokens;
    mapping(uint256 => AuctionItem) private tokenIdToAuction;

    // Constructor to set the fee collector address
    constructor(address _feeCollector) ERC721("NFTMarketplace", "NFTM") {
        owner = payable(msg.sender);
        feeCollector = _feeCollector;
    }

    function updateListPrice(uint256 _listPrice) external payable {
        require(owner == msg.sender, "Only owner can update listing price");
        listPrice = _listPrice;
    }

    // Function to withdraw listing fees
    function withdrawListingFees(uint256 amount) external {
        require(msg.sender == feeCollector, "Only fee collector can withdraw");
        require(amount <= address(this).balance, "Insufficient balance");
        payable(msg.sender).transfer(amount);
        emit ListingFeeWithdrawn(msg.sender, amount);
    }


    function createToken(string memory tokenURI) external payable returns (uint) {
        _tokenIds++;
        uint256 newTokenId = _tokenIds;

        _safeMint(msg.sender, newTokenId);
        _setTokenURI(newTokenId, tokenURI);
        
        unlistedTokens[msg.sender].push(newTokenId);
        
        return newTokenId;
    }

        function listToken(uint256 tokenId, uint256 price) external payable {
        require(unlistedTokens[msg.sender].length > 0, "You don't own any tokens.");
        require(msg.value >= listPrice, "Insufficient funds to list the token.");

        // Deduct listing fee
        if (msg.value > listPrice) {
            payable(feeCollector).transfer(msg.value - listPrice);
        }

        idToListedToken[tokenId] = ListedToken(tokenId, payable(address(0)), payable(msg.sender), price, true);
        uint256 index = findTokenIndex(unlistedTokens[msg.sender], tokenId);
        unlistedTokens[msg.sender][index] = unlistedTokens[msg.sender][unlistedTokens[msg.sender].length - 1];
        unlistedTokens[msg.sender].pop();
        listedTokens[msg.sender].push(tokenId);
        allListedTokens.push(tokenId);

        emit TokenListedSuccess(
            tokenId,
            address(0),
            msg.sender,
            price,
            true
        );
    }

    function getMyUnlistedToken() external view returns (uint256[] memory) {
        console.log(msg.sender);
        // require(unlistedTokens[msg.sender].length > 0, "You don't own any tokens.");
        return unlistedTokens[msg.sender];
    }

    function getMyListedToken() external view returns (uint256[] memory) {
        console.log(msg.sender);
        // require(listedTokens[msg.sender].length > 0, "You don't own any tokens.");
        return listedTokens[msg.sender];

    }

    function getAllListedNFTs() external view returns (uint256[] memory) {
        return allListedTokens;
    }

    function purchaseToken(uint256 tokenId) external payable {
        ListedToken storage token = idToListedToken[tokenId];
        require(token.currentlyListed, "Token is not currently listed for sale.");
        require(msg.value >= token.price, "Insufficient funds to purchase the token.");

        _transfer(token.seller, msg.sender, tokenId);
        token.seller.transfer(token.price);
        token.currentlyListed = false;
        
        removeTokenFromLists(tokenId, token.seller);
        addTokenToUnlisted(msg.sender,tokenId);
    }

    function startAuction(uint256 tokenId, uint256 startPrice, uint256 duration) external {
        require(ownerOf(tokenId) == msg.sender, "You don't own this token.");
        require(startPrice > 0, "Start price must be greater than zero.");

        uint256 endTime = block.timestamp + duration;
        AuctionItem storage auctionItem = tokenIdToAuction[tokenId];
        auctionItem.tokenId = tokenId;
        auctionItem.seller = msg.sender;
        auctionItem.startPrice = startPrice;
        auctionItem.highestBid = 0;
        auctionItem.highestBidder = payable(address(0));
        auctionItem.auctionEndTime = endTime;
        auctionItem.active = true;

        emit AuctionStarted(tokenId, msg.sender, startPrice, endTime);
    }

    function placeBid(uint256 tokenId) external payable {

        AuctionItem storage auctionItem = tokenIdToAuction[tokenId];
        require(auctionItem.active, "Auction not active.");
        require(msg.value > auctionItem.highestBid, "Bid must be higher than current highest bid.");
        require(msg.sender != auctionItem.seller, "You cannot bid on your own auction.");

        // Transfer previous highest bid amount back to the previous highest bidder
        if (auctionItem.highestBidder != address(0)) {
            auctionItem.highestBidder.transfer(auctionItem.highestBid);
        }

        // Store the bid with the bidder's address, amount, and timestamp
        Bid memory newBid = Bid({
            bidder: msg.sender,
            amount: msg.value,
            timestamp: block.timestamp
        });
        auctionItem.bids.push(newBid);

        // Update highest bid with the new bid amount and bidder
        auctionItem.highestBid = msg.value;
        auctionItem.highestBidder = payable(msg.sender);

        emit BidPlaced(tokenId, msg.sender, msg.value);
    }

    function endAuction(uint256 tokenId) external {
        AuctionItem storage auctionItem = tokenIdToAuction[tokenId];
        require(auctionItem.active, "Auction not active.");
        require(block.timestamp >= auctionItem.auctionEndTime, "Auction not ended yet.");
        require(msg.sender == auctionItem.seller, "Only auction owner can end the auction");
    
        // Transfer the token to the highest bidder if exists
        if (auctionItem.highestBidder != address(0)) {
            _transfer(auctionItem.seller, auctionItem.highestBidder, tokenId);
            payable(auctionItem.seller).transfer(auctionItem.highestBid);
            addTokenToUnlisted(auctionItem.highestBidder, tokenId);
        }
    
        // Update auction status and token lists
        auctionItem.active = false;
        removeTokenFromLists(tokenId, auctionItem.seller);
        
        // Clear all bids associated with the token ID
        clearAllBids(tokenId);

        emit AuctionEnded(tokenId, auctionItem.seller, auctionItem.highestBidder, auctionItem.highestBid);
    }

    function clearAllBids(uint256 tokenId) internal {
        AuctionItem storage auctionItem = tokenIdToAuction[tokenId];
        delete auctionItem.bids; // This will clear all bids associated with the token ID
    }

  
    function getHighestBid(uint256 tokenId) external view returns (uint256) {
        AuctionItem storage auctionItem = tokenIdToAuction[tokenId];
        return auctionItem.highestBid;
    }

    function getListedTokenDetails(uint256 tokenId) external view returns (
        uint256,
        address,
        address,
        uint256,
        bool
    ) {
        ListedToken storage token = idToListedToken[tokenId];
        return (
            token.tokenId,
            token.owner,
            token.seller,
            token.price,
            token.currentlyListed
        );
    }

    function getAuctionDetails(uint256 tokenId) external view returns (
        uint256,
        address,
        uint256,
        uint256,
        address,
        uint256,
        bool,
        Bid[] memory
    ) {
        AuctionItem storage auctionItem = tokenIdToAuction[tokenId];
        return (
            auctionItem.tokenId,
            auctionItem.seller,
            auctionItem.startPrice,
            auctionItem.highestBid,
            auctionItem.highestBidder,
            auctionItem.auctionEndTime,
            auctionItem.active,
            auctionItem.bids
        );
    }

    function getAllBids(uint256 tokenId) external view returns (address[] memory, uint256[] memory, uint256[] memory) {
        AuctionItem storage auctionItem = tokenIdToAuction[tokenId];
        uint256 length = auctionItem.bids.length;
        address[] memory bidders = new address[](length);
        uint256[] memory amounts = new uint256[](length);
        uint256[] memory timestamps = new uint256[](length);
        for (uint256 i = 0; i < length; i++) {
            bidders[i] = auctionItem.bids[i].bidder;
            amounts[i] = auctionItem.bids[i].amount;
            timestamps[i] = auctionItem.bids[i].timestamp;
        }
        return (bidders, amounts, timestamps);
    }

    function findTokenIndex(uint256[] memory array, uint256 tokenId) internal pure returns (uint256) {
        for (uint256 i = 0; i < array.length; i++) {
            if (array[i] == tokenId) {
                return i;
            }
        }
        return array.length;
    }
    
    
    function removeTokenFromLists(uint256 tokenId, address seller) internal {
        uint256 index = findTokenIndex(listedTokens[seller], tokenId);
        listedTokens[seller][index] = listedTokens[seller][listedTokens[seller].length - 1];
        listedTokens[seller].pop();
        index = findTokenIndex(allListedTokens, tokenId);
        allListedTokens[index] = allListedTokens[allListedTokens.length - 1];
        allListedTokens.pop();
    }

    function addTokenToUnlisted(address buyer, uint256 tokenId) internal {
        unlistedTokens[buyer].push(tokenId);
    }

}