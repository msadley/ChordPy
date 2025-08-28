from edadht.local_node import ChordNode, in_interval, KEY_SPACE
import unittest
from typing import List

class TestChordDHT(unittest.TestCase):
    """Test suite for Chord DHT implementation"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.single_node = ChordNode("node0")
        
    def test_node_creation_and_hashing(self):
        """Test node creation and hash function consistency"""
        node1 = ChordNode("test_node_1")
        node2 = ChordNode("test_node_2")
        
        # Test that nodes have valid IDs
        self.assertIsInstance(node1.id, int)
        self.assertIsInstance(node2.id, int)
        
        # Test that IDs are within the key space
        self.assertGreaterEqual(node1.id, 0)
        self.assertGreaterEqual(node2.id, 0)
        self.assertLess(node1.id, 2**KEY_SPACE)
        self.assertLess(node2.id, 2**KEY_SPACE)
        
        # Test hash function consistency
        self.assertEqual(node1.hash("test_key"), node1.hash("test_key"))
        
        # Test different keys produce different hashes (with high probability)
        hash1 = node1.hash("key1")
        hash2 = node1.hash("key2")
        self.assertNotEqual(hash1, hash2)  # Very likely to be different

    def test_single_node_operations(self):
        """Test operations on a single node (ring with one node)"""
        node = ChordNode("single")
        node.join()  # Join empty ring
        
        # Test basic structure
        self.assertEqual(node.prev, node)
        self.assertEqual(node.next, node)
        
        # Test put and get operations
        node.put("key1", "value1")
        node.put("key2", "value2")
        
        self.assertEqual(node.get("key1"), "value1")
        self.assertEqual(node.get("key2"), "value2")
        self.assertEqual(node.get("nonexistent"), "Key not found")
        
        # Test finger table
        self.assertIsNotNone(node.finger_table)
        for i in range(KEY_SPACE):
            self.assertEqual(node.finger_table[i], node)

    def test_two_node_ring(self):
        """Test ring with two nodes"""
        node1 = ChordNode("node1")
        node2 = ChordNode("node2")
        
        # Create ring
        node1.join()
        node2.join(node1)
        
        # Test ring structure
        self.assertEqual(node1.next, node2)
        self.assertEqual(node2.next, node1)
        self.assertEqual(node1.prev, node2)
        self.assertEqual(node2.prev, node1)
        
        # Test data operations
        node1.put("key1", "value1")
        node1.put("key2", "value2")
        
        # Both nodes should be able to retrieve all keys
        self.assertEqual(node1.get("key1"), "value1")
        self.assertEqual(node1.get("key2"), "value2")
        self.assertEqual(node2.get("key1"), "value1")
        self.assertEqual(node2.get("key2"), "value2")

    def test_multi_node_ring(self):
        """Test ring with multiple nodes"""
        nodes = [ChordNode(f"node{i}") for i in range(4)]
        
        # Create ring
        nodes[0].join()
        for i in range(1, 4):
            nodes[i].join(nodes[0])
        
        # Test that all nodes are connected
        visited = set()
        current = nodes[0]
        for _ in range(10):  # Prevent infinite loop
            if current.id in visited:
                break
            visited.add(current.id)
            current = current.next
        
        # Should visit all nodes
        self.assertEqual(len(visited), 4)
        
        # Test data distribution and retrieval
        test_keys = ["key1", "key2", "key3", "key4", "key5"]
        test_values = ["val1", "val2", "val3", "val4", "val5"]
        
        # Put data from different nodes
        for i, (key, value) in enumerate(zip(test_keys, test_values)):
            nodes[i % len(nodes)].put(key, value)
        
        # Verify all data can be retrieved from any node
        for start_node in nodes:
            for key, expected_value in zip(test_keys, test_values):
                self.assertEqual(start_node.get(key), expected_value)

    def test_data_transfer_on_join(self):
        """Test that data is properly transferred when a new node joins"""
        # Create initial ring with data
        node1 = ChordNode("initial")
        node1.join()
        
        # Add some data
        test_data = {
            "apple": "fruit",
            "banana": "fruit", 
            "carrot": "vegetable",
            "dog": "animal"
        }
        
        for key, value in test_data.items():
            node1.put(key, value)
        
        # All data should be on node1
        initial_data_count = len(node1.data)
        self.assertGreater(initial_data_count, 0)
        
        # Add a new node
        node2 = ChordNode("joiner")
        node2.join(node1)
        
        # Data should be distributed between nodes
        total_data_after = len(node1.data) + len(node2.data)
        self.assertEqual(total_data_after, len(test_data))
        
        # All data should still be retrievable
        for key, expected_value in test_data.items():
            self.assertEqual(node1.get(key), expected_value)
            self.assertEqual(node2.get(key), expected_value)

    def test_stabilize_operation(self):
        """Test the stabilize operation"""
        nodes = [ChordNode(f"stable{i}") for i in range(3)]
        
        # Create ring
        nodes[0].join()
        nodes[1].join(nodes[0])
        nodes[2].join(nodes[0])
        
        # Run stabilize on all nodes
        for node in nodes:
            node.stabilize()
        
        # Verify ring integrity
        visited_ids = set()
        current = nodes[0]
        for _ in range(10):  # Prevent infinite loop
            if current.id in visited_ids:
                break
            visited_ids.add(current.id)
            # Check that prev/next pointers are consistent
            self.assertEqual(current.next.prev, current)
            current = current.next
        
        self.assertEqual(len(visited_ids), 3)

    def test_finger_table_correctness(self):
        """Test finger table construction and updates"""
        nodes = [ChordNode(f"finger{i}") for i in range(4)]
        
        # Create ring
        nodes[0].join()
        for i in range(1, 4):
            nodes[i].join(nodes[0])
        
        # Update finger tables
        for node in nodes:
            node.update_finger_table(nodes[0])
        
        # Test finger table structure
        for node in nodes:
            # Should have entries for all positions
            self.assertEqual(len(node.finger_table), KEY_SPACE)
            
            # All finger entries should point to valid nodes
            for i in range(KEY_SPACE):
                finger_node = node.finger_table[i]
                self.assertIsInstance(finger_node, ChordNode)
                self.assertIn(finger_node, nodes)

    def test_in_interval_function(self):
        """Test the interval checking function"""
        # Test normal interval (no wrap-around)
        self.assertTrue(in_interval(3, 1, 5))
        self.assertTrue(in_interval(1, 1, 5))  # Inclusive start
        self.assertFalse(in_interval(5, 1, 5))  # Exclusive end
        self.assertFalse(in_interval(0, 1, 5))
        self.assertFalse(in_interval(6, 1, 5))
        
        # Test wrap-around interval
        self.assertTrue(in_interval(7, 6, 2))  # 7 >= 6
        self.assertTrue(in_interval(0, 6, 2))  # 0 < 2
        self.assertTrue(in_interval(1, 6, 2))  # 1 < 2
        self.assertFalse(in_interval(2, 6, 2))  # 2 == end (exclusive)
        self.assertFalse(in_interval(3, 6, 2))
        self.assertFalse(in_interval(5, 6, 2))

    def test_find_successor(self):
        """Test the find_successor algorithm"""
        nodes = [ChordNode(f"succ{i}") for i in range(3)]
        
        # Create a small ring
        nodes[0].join()
        nodes[1].join(nodes[0])
        nodes[2].join(nodes[0])
        
        # Test that find_successor returns valid nodes
        for node in nodes:
            for test_key in range(2**KEY_SPACE):
                successor = node.find_successor(test_key)
                self.assertIsInstance(successor, ChordNode)
                self.assertIn(successor, nodes)

    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        node = ChordNode("edge")
        
        # Test operations on uninitialized node
        result = node.get("test_key")
        self.assertEqual(result, "Key not found")
        
        # Test with empty strings
        node.put("", "empty_key")
        self.assertEqual(node.get(""), "empty_key")
        
        # Test with long strings
        long_key = "a" * 1000
        long_value = "b" * 1000
        node.put(long_key, long_value)
        self.assertEqual(node.get(long_key), long_value)

    def test_concurrent_operations(self):
        """Test behavior under concurrent-like operations"""
        nodes = [ChordNode(f"concurrent{i}") for i in range(3)]
        
        # Build ring
        nodes[0].join()
        nodes[1].join(nodes[0])
        nodes[2].join(nodes[0])
        
        # Simulate concurrent puts from different nodes
        operations = [
            (nodes[0], "key1", "value1"),
            (nodes[1], "key2", "value2"),
            (nodes[2], "key3", "value3"),
            (nodes[0], "key4", "value4"),
            (nodes[1], "key1", "updated_value1"),  # Update existing key
        ]
        
        for node, key, value in operations:
            node.put(key, value)
        
        # Verify final state
        self.assertEqual(nodes[0].get("key1"), "updated_value1")
        self.assertEqual(nodes[1].get("key2"), "value2")
        self.assertEqual(nodes[2].get("key3"), "value3")
        self.assertEqual(nodes[0].get("key4"), "value4")

    def test_ring_consistency_after_multiple_joins(self):
        """Test that ring remains consistent after multiple node joins"""
        # Start with one node
        first_node = ChordNode("first")
        first_node.join()
        
        nodes = [first_node]
        
        # Add nodes one by one
        for i in range(1, 5):
            new_node = ChordNode(f"node{i}")
            new_node.join(first_node)
            nodes.append(new_node)
            
            # After each join, verify ring consistency
            self._verify_ring_consistency(nodes)

    def _verify_ring_consistency(self, nodes: List[ChordNode]):
        """Helper method to verify ring consistency"""
        # Check that we can traverse the entire ring
        visited = set()
        current = nodes[0]
        
        while current.id not in visited:
            visited.add(current.id)
            # Check prev/next consistency
            self.assertEqual(current.next.prev, current,
                           f"Inconsistent pointers at node {current.id}")
            current = current.next
        
        # Should have visited all nodes
        self.assertEqual(len(visited), len(nodes),
                        f"Ring traversal visited {len(visited)} nodes, expected {len(nodes)}")


class TestChordDHTPerformance(unittest.TestCase):
    """Performance and stress tests for Chord DHT"""
    
    def test_lookup_performance(self):
        """Test that lookups complete in reasonable time"""
        import time
        
        # Create larger ring
        nodes = [ChordNode(f"perf{i}") for i in range(8)]
        nodes[0].join()
        for i in range(1, 8):
            nodes[i].join(nodes[0])
        
        # Add data
        for i in range(20):
            nodes[i % len(nodes)].put(f"key{i}", f"value{i}")
        
        # Time lookups
        start_time = time.time()
        for i in range(20):
            result = nodes[0].get(f"key{i}")
            self.assertEqual(result, f"value{i}")
        
        end_time = time.time()
        lookup_time = end_time - start_time
        
        # Should complete quickly (adjust threshold as needed)
        self.assertLess(lookup_time, 1.0, "Lookups took too long")

if __name__ == '__main__':
    unittest.main(verbosity=2)