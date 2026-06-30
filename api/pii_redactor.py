import re

class PIIRedactor:
    """
    DPDP Privacy Vault: Redacts sensitive Indian PII from text.
    Targeted for 'Privy' alignment.
    """
    def __init__(self):
        # Regex for Aadhaar (12 digits, optional spaces/hyphens)
        self.aadhaar_regex = re.compile(r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b')
        # Regex for PAN Card (5 letters, 4 digits, 1 letter)
        self.pan_regex = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b', re.IGNORECASE)
        # Regex for Indian Phone Numbers (+91 or just 10 digits)
        self.phone_regex = re.compile(r'\b(?:\+91[\-\s]?)?[6789]\d{9}\b')
        # Basic Email Regex
        self.email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')

    def redact(self, text: str) -> str:
        if not text:
            return text
            
        redacted = text
        redacted = self.aadhaar_regex.sub('[REDACTED_AADHAAR]', redacted)
        redacted = self.pan_regex.sub('[REDACTED_PAN]', redacted)
        redacted = self.phone_regex.sub('[REDACTED_PHONE]', redacted)
        redacted = self.email_regex.sub('[REDACTED_EMAIL]', redacted)
        
        return redacted

# Singleton instance
redactor = PIIRedactor()
