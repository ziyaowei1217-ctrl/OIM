import string

class InputValidator:
    def __init__(self, text):
        self.text = text.strip()

    def is_long_enough(self, min_chars=20):
        return len(self.text) >= min_chars

    def is_safe(self):
        keywords = ['SELECT', 'DELETE', 'INSERT', 'UPDATE', 'DROP', '--', ';']
        for word in keywords:
            if word.lower() in self.text.lower():
                return False
        
        for char in self.text:
            if char in string.punctuation:
                return False
        
        return True

    def validate_all(self):
        if not self.is_long_enough():
            return (False, "Error message for length")
        
        if not self.is_safe():
            return (False, "Error message for safety/punctuation")
        
        return (True, "Input validated successfully.")

if __name__ == "__main__":
    test1 = InputValidator("DROP TABLE users -- this is a long enough string")
    print(f"Test 1: {test1.validate_all()}")


    test2 = InputValidator("Short input;")
    print(f"Test 2: {test2.validate_all()}")


    test3 = InputValidator("This is a perfectly safe and long enough input string")
    print(f"Test 3: {test3.validate_all()}")