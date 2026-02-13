import string

class InputValidator:
    def __init__(self, text) -> None:
        self.text = text.strip()

    def is_long_enough(self, min_chars=20):
        if len(self.text) >= min_chars:
            return True
        else:   
            return False

    def is_safe(self):
        keywords = ['SELECT', 'DELETE', 'INSERT', 'UPDATE', 'DROP', '--', ';']
        for keyword in keywords:
            if keyword.lower() in self.text.lower():
                return False
            elif keyword in self.text:
                return False    
        
        for punctuation in self.text:
            if punctuation in string.punctuation:
                return False
        
        return True

    def validate_all(self):
        if self.is_long_enough()== False:
            return (False, "Error message for length")
        
        if  self.is_safe() == False:
            return (False, "Error message for safety/punctuation")
        else:
            return (True, "Input validated successfully.")

if __name__ == "__main__":
    test1 = InputValidator("SELECT, DELETE, INSERT, UPDATE, DROP, --, or the command separator ;.")
    print(f"Test 1: {test1.validate_all()}")


    test2 = InputValidator("1sda")
    print(f"Test 2: {test2.validate_all()}")


    test3 = InputValidator("This is a safe and long enough input string")
    print(f"Test 3: {test3.validate_all()}")