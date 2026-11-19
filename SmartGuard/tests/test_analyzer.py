import unittest

from app.analyzer import SmartContractAnalyzer


class SmartContractAnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = SmartContractAnalyzer()

    def rule_ids(self, code):
        return {item["rule_id"] for item in self.analyzer.analyze(code)}

    def test_detects_old_solidity_version(self):
        self.assertIn("SG001", self.rule_ids("pragma solidity ^0.5.0;\ncontract Example {}"))

    def test_modern_solidity_version_is_not_flagged(self):
        self.assertNotIn("SG001", self.rule_ids("pragma solidity ^0.8.20;\ncontract Example {}"))

    def test_detects_tx_origin(self):
        code = """
        pragma solidity ^0.8.20;
        contract Example {
            function check(address owner) public view {
                require(tx.origin == owner);
            }
        }
        """
        self.assertIn("SG002", self.rule_ids(code))

    def test_detects_selfdestruct(self):
        code = """
        pragma solidity ^0.8.20;
        contract Example {
            function destroy() public { selfdestruct(payable(msg.sender)); }
        }
        """
        self.assertIn("SG003", self.rule_ids(code))

    def test_detects_possible_reentrancy_pattern(self):
        code = """
        pragma solidity ^0.8.20;
        contract Example {
            uint public balance = 1 ether;
            function withdraw() public {
                msg.sender.call{value: balance}("");
                balance = 0;
            }
        }
        """
        self.assertIn("SG004", self.rule_ids(code))

    def test_safer_order_does_not_trigger_reentrancy_rule(self):
        code = """
        pragma solidity ^0.8.20;
        contract Example {
            uint public balance = 1 ether;
            function withdraw() public {
                uint amount = balance;
                balance = 0;
                (bool success, ) = msg.sender.call{value: amount}("");
                require(success);
            }
        }
        """
        self.assertNotIn("SG004", self.rule_ids(code))

    def test_detects_unchecked_low_level_call(self):
        code = """
        pragma solidity ^0.8.20;
        contract Example {
            function pay(address payable user) public {
                user.call{value: 1 ether}("");
            }
        }
        """
        self.assertIn("SG005", self.rule_ids(code))

    def test_checked_low_level_call_is_not_flagged_as_unchecked(self):
        code = """
        pragma solidity ^0.8.20;
        contract Example {
            function pay(address payable user) public {
                (bool success, ) = user.call{value: 1 ether}("");
                require(success);
            }
        }
        """
        self.assertNotIn("SG005", self.rule_ids(code))

    def test_detects_delegatecall(self):
        code = """
        pragma solidity ^0.8.20;
        contract Example {
            function run(address target, bytes memory data) public {
                target.delegatecall(data);
            }
        }
        """
        self.assertIn("SG006", self.rule_ids(code))

    def test_detects_timestamp_dependency(self):
        code = """
        pragma solidity ^0.8.20;
        contract Example {
            function open(uint deadline) public view {
                require(block.timestamp > deadline);
            }
        }
        """
        self.assertIn("SG007", self.rule_ids(code))

    def test_detects_block_based_randomness(self):
        code = """
        pragma solidity ^0.8.20;
        contract Example {
            function random() public view returns (uint) {
                return uint(keccak256(abi.encodePacked(block.timestamp, blockhash(block.number - 1))));
            }
        }
        """
        self.assertIn("SG008", self.rule_ids(code))

    def test_comments_are_ignored(self):
        code = """
        pragma solidity ^0.8.20;
        contract Example {
            // tx.origin selfdestruct(msg.sender) target.delegatecall(data)
            function ok() public pure returns (uint) { return 1; }
        }
        """
        ids = self.rule_ids(code)
        self.assertNotIn("SG002", ids)
        self.assertNotIn("SG003", ids)
        self.assertNotIn("SG006", ids)


if __name__ == "__main__":
    unittest.main()
