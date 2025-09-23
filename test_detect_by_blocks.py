import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pytest

from processing_line import Transaction
from fraud_detection import FraudDetection

def make_transactions(signatures):
    """Helper: build Transaction objects with given signatures."""
    txs = []
    for i, sig in enumerate(signatures, start=1):
        t = Transaction(i, "Alice", "Bob")
        t.signature = sig
        txs.append(t)
    return txs


def test_identical_signatures():
    # All signatures identical → maximum suspicion
    txs = make_transactions(["aaaa", "aaaa", "aaaa"])
    fd = FraudDetection(txs)
    block_size, score = fd.detect_by_blocks()
    assert score == 27  # 3*3*3, all in one group
    assert 1 <= block_size <= len(txs[0].signature)


def test_two_permutations_blocksize1():
    # Example: 2 signatures that are permutations by block size 1
    txs = make_transactions(["aabbcc", "ccbbaa"])
    fd = FraudDetection(txs)
    block_size, score = fd.detect_by_blocks()
    assert score == 2
    assert block_size in (1, 2)


def test_example_from_description():
    # Example given in problem: abc, acb, xyz, bac, zyx, abb
    txs = make_transactions(["abc", "acb", "xyz", "bac", "zyx", "abb"])
    fd = FraudDetection(txs)
    block_size, score = fd.detect_by_blocks()
    assert (block_size, score) == (1, 6)


def test_with_suffix():
    # Signatures with leftover suffix that cannot move
    txs = make_transactions(["abcdefg", "efcdabg"])
    fd = FraudDetection(txs)
    block_size, score = fd.detect_by_blocks()
    # They should group only under block size 2, suspicion score = 2
    assert score == 2
    assert block_size == 2


def test_no_matches_all_unique():
    # Completely different signatures, no grouping possible
    txs = make_transactions(["abcd", "efgh", "ijkl"])
    fd = FraudDetection(txs)
    block_size, score = fd.detect_by_blocks()
    # suspicion score must be 1 (1x1x1)
    assert score == 1
    assert 1 <= block_size <= len("abcd")


def test_short_signatures_single_char():
    # Signatures of length 1
    txs = make_transactions(["a", "b", "c"])
    fd = FraudDetection(txs)
    block_size, score = fd.detect_by_blocks()
    assert score == 1  # all unique
    assert block_size == 1


def test_large_all_identical():
    # Stress: 10 identical long signatures
    sig = "abcd" * 20
    txs = make_transactions([sig] * 10)
    fd = FraudDetection(txs)
    block_size, score = fd.detect_by_blocks()
    assert score == 10 ** 10  # huge group (one group of size 10)
    assert 1 <= block_size <= len(sig)


def test_large_all_different():
    # Stress: large unique signatures
    txs = make_transactions([f"{i:04d}" for i in range(50)])
    fd = FraudDetection(txs)
    block_size, score = fd.detect_by_blocks()
    assert score == 1  # all unique
