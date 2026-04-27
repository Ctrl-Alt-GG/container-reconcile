#!/usr/bin/env python3
"""
Proxmox LXC Selection Helper Filters
Provides reusable Jinja2 filters for deterministic resource selection
"""

import ipaddress
from typing import Any, Dict, List, Optional


def select_best_node_by_resources(
    nodes: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    Select the best node from a list based on available resources.
    Sorting order: most free memory, then lexical name

    Args:
        nodes: List of node dictionaries with memory and storage info

    Returns:
        The selected node dictionary, or None if list is empty
    """
    if not nodes:
        return None

    # Sort by multiple criteria: memory (desc), then name (asc)
    sorted_nodes = sorted(
        nodes,
        key=lambda x: (-x.get("memory", {}).get("free_bytes", 0), x.get("name", "")),
    )

    return sorted_nodes[0] if sorted_nodes else None


def find_first_available_ip(
    excluded_ips: List[str], subnet_ips: List[str]
) -> Optional[str]:
    """
    Find the first available IP address from a subnet.

    Args:
        excluded_ips: List of IPs to exclude (reserved + in-use)
        subnet_ips: List of all available IPs in subnet

    Returns:
        First available IP address, or None if all are excluded
    """
    excluded_set = set(excluded_ips)
    available = [ip for ip in subnet_ips if ip not in excluded_set]

    if available:
        available.sort(key=ipaddress.ip_address)
        return available[0]

    return None


def find_first_available_vmid(
    used_vmids: List[int], min_vmid: int, max_vmid: int
) -> Optional[int]:
    """
    Find the first available VMID in the managed range.

    Args:
        used_vmids: List of currently used VMID integers
        min_vmid: Minimum VMID in managed range
        max_vmid: Maximum VMID in managed range

    Returns:
        First available VMID integer, or None if range exhausted
    """
    used_set = set(used_vmids)

    for vmid in range(min_vmid, max_vmid + 1):
        if vmid not in used_set:
            return vmid

    return None


def cidr_host_addresses(cidr: str) -> List[str]:
    """
    Return all usable host addresses in a CIDR (excludes network and broadcast).

    Args:
        cidr: IPv4 CIDR string, e.g. "192.168.130.0/24"

    Returns:
        Sorted list of host IP strings.
    """
    network = ipaddress.ip_network(cidr, strict=False)
    return [str(host) for host in network.hosts()]


class FilterModule:
    """Jinja2 Filter Module"""

    def filters(self) -> Dict[str, Any]:
        """
        Return dictionary of filter functions.

        Returns:
            Dictionary mapping filter names to filter functions
        """
        return {
            "select_best_node_by_resources": select_best_node_by_resources,
            "find_first_available_ip": find_first_available_ip,
            "find_first_available_vmid": find_first_available_vmid,
            "cidr_host_addresses": cidr_host_addresses,
        }
