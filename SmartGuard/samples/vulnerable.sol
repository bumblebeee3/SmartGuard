pragma solidity ^0.5.0;

contract VulnerableVault {
    address public owner;
    uint public balance = 5 ether;

    constructor() public {
        owner = msg.sender;
    }

    function adminCheck() public view returns (bool) {
        return tx.origin == owner;
    }

    function withdraw() public {
        msg.sender.call{value: balance}("");
        balance = 0;
    }

    function runExternal(address target, bytes memory data) public {
        target.delegatecall(data);
    }

    function deadlineReached(uint deadline) public view returns (bool) {
        return block.timestamp > deadline;
    }

    function pseudoRandom() public view returns (uint) {
        return uint(keccak256(abi.encodePacked(block.timestamp, blockhash(block.number - 1)))) % 100;
    }

    function destroy() public {
        selfdestruct(msg.sender);
    }
}
