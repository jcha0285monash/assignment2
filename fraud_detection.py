
from processing_line import Transaction
from data_structures import ArrayR
from data_structures import HashTableSeparateChaining
from data_structures import LinkedList
from algorithms import insertion_sort
from data_structures.hash_table_linear_probing import LinearProbeTable


class FraudDetection:
    def __init__(self, transactions):
        self.transactions = transactions

    def detect_by_blocks(self):
        """
        Analyse your time complexity of this method.
        :complexity: Best case is O(N * L^2) where N is the number of transactions and L is the 
        length of a signature.
        
        The best case happens when the block size S is large (close to the length of a signature), 
        so each signature only splits into a small number of blocks. In this case, insertion sort 
        works on very few blocks, and the cost per transaction is dominated by string slicing and 
        hashing, both of which are O(L). Over all block sizes, this totals to O(N * L^2).

        Worst case is O(N * L^3). This happens when the block size S = 1, so each signature of length 
        L is split into L single-character blocks. Insertion sort must then sort L blocks, which costs 
        O(L^2) per transaction. Since there are N transactions and up to L different block sizes to 
        test, the total becomes O(N * L^3).
        """
        first_signature = self.transactions[0].signature
        raw_signature_length = len(first_signature)

        best_score_block_size = 1
        best_score = 1

        # Try all block sizes
        for S in range(1, raw_signature_length + 1):
            table = HashTableSeparateChaining()

            # For each transaction sort the blocks and add to hash table to find how many transactions match
            for transaction in self.transactions:
                signature = transaction.signature
                signature_length = (raw_signature_length // S) * S
                prefix = signature[:signature_length]
                suffix = signature[signature_length:]

                # Split the signature into blocks
                blocks = LinkedList()
                for i in range(0, signature_length, S):
                    blocks.append(prefix[i:i+S])

                # Insertion sort
                sorted_blocks = insertion_sort(blocks)
                duplicates = "".join(sorted_blocks) + suffix

                # Increment duplicate count in hash table
                try:
                    curr = table[duplicates]
                    table[duplicates] = curr + 1
                except KeyError:
                    table[duplicates] = 1

            # Calculate suspicion score
            items = table.items()
            score = 1
            for j in range(len(items)):
                key, value = items[j]
                score *= value

            # Update best score
            if score > best_score:
                best_score = score
                best_score_block_size = S

        return (best_score_block_size, best_score)

    def rectify(self, functions):
        best_func = None
        best_mpcl = float("inf")

        for f in functions:
            table = LinearProbeTable()
            max_chain = 0

            # Insert each transaction's key
            for tx in self.transactions:
                key = str(f(tx))
                probe_chain = 0
                position = table.hash(key)

                # count probes until empty slot or match
                while True:
                    if table._LinearProbeTable__array[position] is None:
                        break
                    elif table._LinearProbeTable__array[position][0] == key:
                        break
                    else:
                        probe_chain += 1
                        position = (position + 1) % table.table_size

                # update MPCL
                max_chain = max(max_chain, probe_chain)
                table[key] = tx.timestamp

            if max_chain < best_mpcl:
                best_mpcl = max_chain
                best_func = f

        return (best_func, best_mpcl)



if __name__ == "__main__":
    # Write tests for your code here...
    # We are not grading your tests, but we will grade your code with our own tests!
    # So writing tests is a good idea to ensure your code works as expected.
    
    def to_array(lst):
        """
        Helper function to create an ArrayR from a list.
        """
        lst = [to_array(item) if isinstance(item, list) else item for item in lst]
        return ArrayR.from_list(lst)

    # Here is something to get you started with testing detect_by_blocks
    print("<------- Testing detect_by_blocks! ------->")
    # Let's create 2 transactions and set their signatures
    tr1 = Transaction(1, "Alice", "Bob")
    tr2 = Transaction(2, "Alice", "Bob")

    # I will intentionally give the signatures that would put them in the same groups
    # if the block size was 1 or 2.
    tr1.signature = "aabbcc"
    tr2.signature = "ccbbaa"

    # Let's create an instance of FraudDetection with these transactions
    fd = FraudDetection([tr1, tr2])

    # Let's test the detect_by_blocks method
    block_size, suspicion_score = fd.detect_by_blocks()

    # We print the result, hopefully we should see either 1 or 2 for block size, and 2 for suspicion score.
    print(f"Block size: {block_size}, Suspicion score: {suspicion_score}")

    # I'm putting this line here so you can find where the testing ends in the terminal, but testing is by no means
    # complete. There are many more scenarios you'll need to test. Follow what we did above.
    print("<--- Testing detect_by_blocks finished! --->\n")

    # ----------------------------------------------------------

    # Here is something to get you started with testing rectify
    print("<------- Testing rectify! ------->")
    # I'm creating 4 simple transactions...
    transactions = [
        Transaction(1, "Alice", "Bob"),
        Transaction(2, "Alice", "Bob"),
        Transaction(3, "Alice", "Bob"),
        Transaction(4, "Alice", "Bob"),
    ]

    # Then I create two functions and to make testing easier, I use the timestamps I
    # gave to transactions to return the value I want for each transaction.
    def function1(transaction):
        return [2, 1, 1, 50][transaction.timestamp - 1]

    def function2(transaction):
        return [1, 2, 3, 4][transaction.timestamp - 1]

    # Now I create an instance of FraudDetection with these transactions
    fd = FraudDetection(to_array(transactions))

    # And I call rectify with the two functions
    result = fd.rectify(to_array([function1, function2]))

    # The expected result is (function2, 0) because function2 will give us a max probe chain of 0.
    # This is the same example given in the specs
    print(result)
    
    # I'll also use an assert statement to make sure the returned function is indeed the correct one.
    # This will be harder to verify by printing, but can be verified easily with an `assert`:
    assert result == (function2, 0), f"Expected (function2, 0), but got {result}"

    print("<--- Testing rectify finished! --->")