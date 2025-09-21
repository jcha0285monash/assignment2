from data_structures.linked_stack import LinkedStack
from data_structures.linked_queue import LinkedQueue

class Transaction:
    def __init__(self, timestamp, from_user, to_user):
        self.timestamp = timestamp
        self.from_user = from_user
        self.to_user = to_user
        self.signature = None
    
    def sign(self):
        """
        :complexity: O(N + K) where N is the length of the variable string 
        data_string and K is the constant signature length 36.

        Computing data_string is O(1) assuming string formatting 
        uses fixed-size fields. The first loop iterates once per character 
        in data_string, performing O(1) work for each iteration O(N). The second 
        loop runs exactly 36 times (the signature length), performing O(1) 
        each iteration O(K), which is O(1) because K = 36 is constant.

        Overall, the dominant term is O(N).
        Worst case is therefore O(N).
        """
        data_string = f"{self.timestamp}-{self.from_user}-{self.to_user}"
        hash_prime = 2**127-1
        current_hash_value = 0
        hash_base = 37
        
        for char in data_string:
            current_hash_value = (current_hash_value * hash_base + ord(char)) % hash_prime
        
        if current_hash_value < 0:
            current_hash_value += hash_prime
            
        base36_chars = "0123456789abcdefghijklmnopqrstuvwxyz"
        signature_length = 36
        
        base36_string = ""
        temp_hash_value = current_hash_value
        
        for i in range(signature_length):
            base36_string = base36_chars[temp_hash_value % len(base36_chars)] + base36_string
            temp_hash_value //= len(base36_chars)
        
        self.signature = base36_string

class _ProcessingLineIterator:
    def __init__(self, processing_line):
        self.processing_line = processing_line
        self._critical = False
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if not self.processing_line._before_queue.is_empty():
            item = self.processing_line._before_queue.serve()
            item.sign()
            return item
        
        if not self._critical:
            self._critical = True
            item = self.processing_line.critical_transaction
            item.sign()
            return item
        
        if not self.processing_line._after_stack.is_empty():
            item = self.processing_line._after_stack.pop()
            item.sign()
            return item
        
        raise StopIteration

class ProcessingLine:
    def __init__(self, critical_transaction):
        """
        Analyse your time complexity of this method.
        """
        self.critical_transaction = critical_transaction
        self._before_queue = LinkedQueue()
        self._after_stack = LinkedStack()
        self._locked = False
        self._iterator_active = False
        
        
    def __iter__(self):
        if self._locked:
            raise RuntimeError("Processing line is locked.")
        self._locked = True
        self._iterator_active = True
        return _ProcessingLineIterator(self)


    def add_transaction(self, transaction):
        """
        Analyse your time complexity of this method.
        """
        if self._locked:
            raise RuntimeError("Processing line is locked.")
        
        if transaction.timestamp <= self.critical_transaction.timestamp:
            self._before_queue.append(transaction)
        else:
            self._after_stack.push(transaction)

if __name__ == "__main__":
    # Write tests for your code here...
    # We are not grading your tests, but we will grade your code with our own tests!
    # So writing tests is a good idea to ensure your code works as expected.
    
    # Here's something to get you started...
    transaction1 = Transaction(50, "alice", "bob")
    transaction2 = Transaction(100, "bob", "dave")
    transaction3 = Transaction(120, "dave", "frank")

    line = ProcessingLine(transaction2)
    line.add_transaction(transaction3)
    line.add_transaction(transaction1)

    print("Let's print the transactions... Make sure the signatures aren't empty!")
    line_iterator = iter(line)
    while True:
        try:
            transaction = next(line_iterator)
            print(f"Processed transaction: {transaction.from_user} -> {transaction.to_user}, "
                  f"Time: {transaction.timestamp}\nSignature: {transaction.signature}")
        except StopIteration:
            break
    