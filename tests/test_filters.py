#!/usr/bin/env python3
"""
Unit tests for Ansible filter plugins
Tests the deterministic selection and allocation logic
"""

import sys
import unittest
from pathlib import Path
from typing import List, Dict, Any

# Add filter_plugins to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'filter_plugins'))

from proxmox_selectors import (
    select_best_node_by_resources,
    find_first_available_ip,
    find_first_available_vmid,
    cidr_host_addresses,
)


class TestNodeSelection(unittest.TestCase):
    """Test node selection logic"""

    def test_select_best_node_empty_list(self) -> None:
        """Test with empty node list"""
        result = select_best_node_by_resources([])
        self.assertIsNone(result)

    def test_select_best_node_single_node(self) -> None:
        """Test with single node"""
        nodes: List[Dict[str, Any]] = [
            {'name': 'pve-01', 'memory': {'free_bytes': 1000000}}
        ]
        result = select_best_node_by_resources(nodes)
        self.assertEqual(result['name'], 'pve-01')

    def test_select_best_node_by_memory(self) -> None:
        """Test selection prioritizes free memory"""
        nodes: List[Dict[str, Any]] = [
            {'name': 'pve-01', 'memory': {'free_bytes': 1000000}},
            {'name': 'pve-02', 'memory': {'free_bytes': 2000000}},
            {'name': 'pve-03', 'memory': {'free_bytes': 500000}},
        ]
        result = select_best_node_by_resources(nodes)
        # Should select pve-02 (highest free memory)
        self.assertEqual(result['name'], 'pve-02')

    def test_select_best_node_by_name_tiebreaker(self) -> None:
        """Test selection uses name as tiebreaker"""
        nodes: List[Dict[str, Any]] = [
            {'name': 'pve-03', 'memory': {'free_bytes': 1000000}},
            {'name': 'pve-01', 'memory': {'free_bytes': 1000000}},
            {'name': 'pve-02', 'memory': {'free_bytes': 1000000}},
        ]
        result = select_best_node_by_resources(nodes)
        # Should select pve-01 (lexically first when memory equal)
        self.assertEqual(result['name'], 'pve-01')
    
    def test_select_best_node_deterministic(self) -> None:
        """Test that selection is deterministic"""
        nodes: List[Dict[str, Any]] = [
            {'name': 'pve-02', 'memory': {'free_bytes': 1500000}},
            {'name': 'pve-01', 'memory': {'free_bytes': 2000000}},
        ]
        result1 = select_best_node_by_resources(nodes)
        result2 = select_best_node_by_resources(nodes)
        self.assertEqual(result1['name'], result2['name'])


class TestIPAllocation(unittest.TestCase):
    """Test IP allocation logic"""

    def test_find_first_available_ip_empty_excluded(self) -> None:
        """Test with no excluded IPs"""
        subnet_ips: List[str] = ['10.0.1.2', '10.0.1.3', '10.0.1.4']
        result = find_first_available_ip([], subnet_ips)
        self.assertEqual(result, '10.0.1.2')

    def test_find_first_available_ip_with_excluded(self) -> None:
        """Test with excluded IPs"""
        subnet_ips: List[str] = ['10.0.1.2', '10.0.1.3', '10.0.1.4', '10.0.1.5']
        excluded: List[str] = ['10.0.1.2', '10.0.1.3']
        result = find_first_available_ip(excluded, subnet_ips)
        self.assertEqual(result, '10.0.1.4')

    def test_find_first_available_ip_all_excluded(self) -> None:
        """Test when all IPs are excluded"""
        subnet_ips: List[str] = ['10.0.1.2', '10.0.1.3']
        excluded: List[str] = ['10.0.1.2', '10.0.1.3']
        result = find_first_available_ip(excluded, subnet_ips)
        self.assertIsNone(result)

    def test_find_first_available_ip_sorted_order(self) -> None:
        """Test that IPs are returned in sorted order"""
        subnet_ips: List[str] = ['10.0.1.5', '10.0.1.2', '10.0.1.4', '10.0.1.3']
        result = find_first_available_ip([], subnet_ips)
        # Should return smallest IP
        self.assertEqual(result, '10.0.1.2')

    def test_find_first_available_ip_deterministic(self) -> None:
        """Test that selection is deterministic"""
        subnet_ips: List[str] = ['10.0.1.5', '10.0.1.2', '10.0.1.4']
        excluded: List[str] = ['10.0.1.5']
        result1 = find_first_available_ip(excluded, subnet_ips)
        result2 = find_first_available_ip(excluded, subnet_ips)
        self.assertEqual(result1, result2)


class TestVMIDAllocation(unittest.TestCase):
    """Test VMID allocation logic"""

    def test_find_first_available_vmid_empty_used(self) -> None:
        """Test with no used VMIDs"""
        result = find_first_available_vmid([], 100, 105)
        self.assertEqual(result, 100)

    def test_find_first_available_vmid_with_used(self) -> None:
        """Test with some used VMIDs"""
        used: List[int] = [100, 101, 102]
        result = find_first_available_vmid(used, 100, 105)
        self.assertEqual(result, 103)

    def test_find_first_available_vmid_range_exhausted(self) -> None:
        """Test when range is exhausted"""
        used: List[int] = [100, 101, 102, 103, 104, 105]
        result = find_first_available_vmid(used, 100, 105)
        self.assertIsNone(result)

    def test_find_first_available_vmid_gap_in_middle(self) -> None:
        """Test with gap in the middle"""
        used: List[int] = [100, 102, 104]
        result = find_first_available_vmid(used, 100, 105)
        self.assertEqual(result, 101)

    def test_find_first_available_vmid_deterministic(self) -> None:
        """Test that selection is deterministic"""
        used: List[int] = [100, 102]
        result1 = find_first_available_vmid(used, 100, 105)
        result2 = find_first_available_vmid(used, 100, 105)
        self.assertEqual(result1, result2)


class TestDeterminism(unittest.TestCase):
    """Test that selection functions are deterministic"""

    def test_multiple_runs_same_selection(self) -> None:
        """Test that same inputs always produce same output"""
        nodes: List[Dict[str, Any]] = [
            {'name': 'pve-02', 'memory': {'free_bytes': 1500000}},
            {'name': 'pve-01', 'memory': {'free_bytes': 2000000}},
            {'name': 'pve-03', 'memory': {'free_bytes': 1000000}},
        ]

        results = [select_best_node_by_resources(nodes) for _ in range(5)]
        selected_names = [r['name'] for r in results]

        # All selections should be identical
        self.assertEqual(len(set(selected_names)), 1)
        self.assertEqual(selected_names[0], 'pve-01')


class TestCIDRHosts(unittest.TestCase):
    """Test CIDR host expansion behavior"""

    def test_cidr_hosts_excludes_network_and_broadcast(self) -> None:
        """A /30 should return only two usable host addresses"""
        result = cidr_host_addresses('192.168.1.0/30')
        self.assertEqual(result, ['192.168.1.1', '192.168.1.2'])

    def test_cidr_hosts_for_24_starts_at_first_host(self) -> None:
        """A /24 should start at .1 and end at .254"""
        result = cidr_host_addresses('10.0.1.0/24')
        self.assertEqual(result[0], '10.0.1.1')
        self.assertEqual(result[-1], '10.0.1.254')
        self.assertEqual(len(result), 254)


def main() -> int:
    """Run all tests"""
    print("=" * 60)
    print("Testing Filter Plugin Functions")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestNodeSelection))
    suite.addTests(loader.loadTestsFromTestCase(TestIPAllocation))
    suite.addTests(loader.loadTestsFromTestCase(TestVMIDAllocation))
    suite.addTests(loader.loadTestsFromTestCase(TestDeterminism))
    suite.addTests(loader.loadTestsFromTestCase(TestCIDRHosts))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 60)

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
