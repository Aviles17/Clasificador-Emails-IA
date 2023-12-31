import re

class email_message:
    #Create constructor of the class
    def __init__(self, id: str, subject: str, by: str, snippet: str, message: list, label: int = None):
        
        self.id = id
        self.subject = subject
        self.snippet = snippet
        self.message = message
        name, email = self.decompose(by)
        self.by_name = name
        self.by_email = email
        self.label = label
    
    #Define '==' behavior for the class objects
    def __eq__(self, other):
        return isinstance(other, email_message) and self.id == other.id
    
    #Define how does the str function works
    def __str__(self):
        return f'''ID: {self.id},
     
Subject: {self.subject} 

By: {self.by_name} 

ByEmail: {self.by_email}
 
Snippet: {self.snippet} 

Message: {self.message}'''

    #Define decompose function
    def decompose(self, by: str):
        if '<' in by:
            parts = by.split('<')
            name = parts[0].strip()
            email = self.get_domain(parts[1][:-1])
            return name, email
        else:
            return by, by
        
    def get_domain(self, email: str):
        pattern = r'@([\w.-]+)'
        match = re.search(pattern, email)
        if match:
            # Extract the domain
            domain = match.group(1)
            return domain
        else:
            return email
    
    def check_data_integrity(self):
        if self.by_email == self.by_name:
            if '@' in self.by_email:
                self.by_name = None
            else:
                self.by_email = None
        