from data_structures import ArrayR

from processing_line import Transaction


class ProcessingBook:
    LEGAL_CHARACTERS = "abcdefghijklmnopqrstuvwxyz0123456789"

    def __init__(self, level=0):
        self.pages = ArrayR(len(ProcessingBook.LEGAL_CHARACTERS))
        self.level = level
        self.error_count = 0
        self.count = 0
    
    def page_index(self, character):
        """
        You may find this method helpful. It takes a character and returns the index of the relevant page.
        Time complexity of this method is O(1), because it always only checks 36 characters.
        """
        return ProcessingBook.LEGAL_CHARACTERS.index(character)
    
    def get_error_count(self):
        """
        Returns the number of errors encountered while storing transactions.
        """
        return self.error_count 
    
    def __len__(self):
        return self.count
    
    def _extract_single(self):
        single = None
        for page in self.pages:
            if page is not None:
                if single is not None:
                    return None
                if isinstance(page, tuple):
                    single = page
                elif isinstance(page, ProcessingBook):
                    extracted = page._extract_single()
                    if extracted is None:
                        return None
                    single = extracted
        return single
    
    def __delitem__(self, transaction):
        signature = transaction.signature
        index = self.page_index(signature[self.level])
        current = self.pages[index]
        
        if current is None:
            raise KeyError(f"Transaction {signature} not found")
        
        if isinstance(current, tuple):
            existing_transaction, existing_amount = current
            if existing_transaction.signature == signature:
                self.pages[index] = None
                self.count -= 1
                return
            else:
                raise KeyError(f"Transaction {signature} not found")
        
        if isinstance(current, ProcessingBook):
            before = len(current)
            del current[transaction]
            after = len(current)
            self.count -= (before - after)
            
            if after == 0:
                self.pages[index] = None
            elif after == 1:
                extracted = current._extract_single()
                if extracted is not None:
                    self.pages[index] = extracted
            return
        
        raise KeyError(f"Transaction {signature} not found")
    
    def __setitem__(self, transaction, amount):
        signature = transaction.signature
        if len(signature) <= self.level:
            self.error_count += 1
            return
        
        index = self.page_index(signature[self.level])
        current = self.pages[index]
        
        if current is None:
            self.pages[index] = (transaction, amount)
            self.count += 1
            return
        
        if isinstance(current, tuple):
            existing_transaction, existing_amount = current
            if existing_transaction.signature == signature:
                if existing_amount != amount:
                    self.error_count += 1
                return
            else:
                nested = ProcessingBook(self.level + 1)
                nested[existing_transaction] = existing_amount
                nested[transaction] = amount
                self.pages[index] = nested
                self.count += 1
                return
        
        if isinstance(current, ProcessingBook):
            before_error = current.get_error_count()
            before_count = len(current)
            current[transaction] = amount
            after_error = current.get_error_count()
            after_count = len(current)
            
            self.error_count += (after_error - before_error)
            self.count += (after_count - before_count)
            return
        
    def __getitem__(self, transaction):
        signature = transaction.signature
        index = self.page_index(signature[self.level])
        current = self.pages[index]
        
        if current is None:
            raise KeyError(f"Transaction {signature} not found")
        
        if isinstance(current, tuple):
            existing_transaction, amount = current
            if existing_transaction.signature == signature:
                return amount
            else:
                raise KeyError(f"Transaction {signature} not found")
        
        if isinstance(current, ProcessingBook):
            return current[transaction]
        
        raise KeyError(f"Transaction {signature} not found")
                
    
    def sample(self, required_size):
        """
        1054 Only - 1008/2085 welcome to attempt if you're up for a challenge, but no marks are allocated.
        Analyse your time complexity of this method.
        """
        pass


if __name__ == "__main__":
    # Write tests for your code here...
    # We are not grading your tests, but we will grade your code with our own tests!
    # So writing tests is a good idea to ensure your code works as expected.

    # Let's create a few transactions
    tr1 = Transaction(123, "sender", "receiver")
    tr1.signature = "abc123"

    tr2 = Transaction(124, "sender", "receiver")
    tr2.signature = "0bbzzz"

    tr3 = Transaction(125, "sender", "receiver")
    tr3.signature = "abcxyz"

    # Let's create a new book to store these transactions
    book = ProcessingBook()

    book[tr1] = 10
    print(book[tr1])  # Prints 10

    book[tr2] = 20
    print(book[tr2])  # Prints 20

    book[tr3] = 30    # Ends up creating 3 other nested books
    print(book[tr3])  # Prints 30
    print(book[tr2])  # Prints 20

    book[tr2] = 40
    print(book[tr2])  # Prints 20 (because it shouldn't update the amount)

    del book[tr1]     # Delete the first transaction. This also means the nested books will be collapsed. We'll test that in a bit.
    try:
        print(book[tr1])  # Raises KeyError
    except KeyError as e:
        print("Raised KeyError as expected:", e)

    print(book[tr2])  # Prints 20
    print(book[tr3])  # Prints 30

    # We deleted T1 a few lines above, which collapsed the nested books.
    # Let's make sure that actually happened. We should be able to find tr3 sitting
    # in Page A of the book:
    print(book.pages[book.page_index('a')])  # This should print whatever details we stored of T3 and only T3
