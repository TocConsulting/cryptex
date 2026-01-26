"""
Password generation engine with cryptographically secure random generation.
"""

import json
import math
import random
import re
import secrets
import uuid
import base64
from typing import Dict, List, Optional, Tuple


class PasswordGenerator:
    """
    Cryptographically secure password generator with advanced customization options.
    """

    def __init__(self):
        self.lowercase = 'abcdefghijklmnopqrstuvwxyz'
        self.uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.digits = '0123456789'
        self.special = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        self.similar = 'il1Lo0O'
        self.min_length = 8
        self.max_length = 256
        self.max_attempts = 1000

    def generate_strong_password(self, length: int, charset: str) -> str:
        """Generate a cryptographically secure random password."""
        if not charset:
            raise ValueError("Character set cannot be empty")
        return ''.join(secrets.choice(charset) for _ in range(length))

    def generate_pronounceable_password(self, length: int) -> str:
        """Generate a pronounceable password with consonant-vowel pattern."""
        consonants = 'bcdfghjklmnpqrstvwxyz'
        vowels = 'aeiou'
        password = ''
        use_consonant = True

        while len(password) < length:
            if use_consonant:
                char = secrets.choice(consonants)
                if secrets.randbelow(3) == 0:
                    char = char.upper()
            else:
                char = secrets.choice(vowels)
            
            password += char
            use_consonant = not use_consonant

        if length >= 10:
            num_position = secrets.randbelow(length - 2) + 1
            number = str(secrets.randbelow(100)).zfill(2)
            password = password[:num_position] + number + password[num_position:]
            password = password[:length]

        return password

    def generate_api_key(self, length: int, api_format: str) -> str:
        """Generate API key in various formats."""
        if api_format == 'uuid':
            return str(uuid.uuid4())
        elif api_format == 'uuid-hex':
            return str(uuid.uuid4()).replace('-', '')
        elif api_format == 'base64':
            # Generate random bytes and encode as base64
            num_bytes = (length * 3) // 4  # Approximate bytes needed for base64
            random_bytes = secrets.token_bytes(num_bytes)
            return base64.b64encode(random_bytes).decode('ascii')[:length]
        elif api_format == 'hex':
            return secrets.token_hex(length // 2)
        elif api_format == 'url-safe':
            return secrets.token_urlsafe(length)[:length]
        elif api_format == 'alphanum':
            charset = self.lowercase + self.uppercase + self.digits
            return self.generate_strong_password(length, charset)
        else:  # default
            charset = self.lowercase + self.uppercase + self.digits
            return self.generate_strong_password(length, charset)

    def validate_password(self, password: str, min_upper: int, min_lower: int, 
                         min_digit: int, min_special: int) -> bool:
        """Validate password meets minimum character requirements."""
        upper_count = sum(1 for c in password if c.isupper())
        lower_count = sum(1 for c in password if c.islower())
        digit_count = sum(1 for c in password if c.isdigit())
        special_count = sum(1 for c in password if not c.isalnum())

        return (upper_count >= min_upper and 
                lower_count >= min_lower and 
                digit_count >= min_digit and 
                special_count >= min_special)

    def calculate_strength(self, password: str) -> Tuple[int, str]:
        """Calculate password strength score and description."""
        length = len(password)
        score = 0

        # Length scoring
        if length >= 8: score += 10
        if length >= 12: score += 10
        if length >= 16: score += 10
        if length >= 20: score += 10

        # Character variety scoring
        if re.search(r'[a-z]', password): score += 10
        if re.search(r'[A-Z]', password): score += 10
        if re.search(r'[0-9]', password): score += 10
        if re.search(r'[^a-zA-Z0-9]', password): score += 20

        # Pattern penalties
        if re.search(r'(.)\1{2,}', password): score -= 10  # Repeated characters
        if re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def)', password): score -= 10

        # Strength classification
        if score >= 70:
            strength = "Very Strong"
        elif score >= 50:
            strength = "Strong"
        elif score >= 30:
            strength = "Moderate"
        else:
            strength = "Weak"

        return score, strength

    def calculate_entropy(self, password: str) -> float:
        """Calculate password entropy in bits."""
        charset_size = 0
        if re.search(r'[a-z]', password): charset_size += 26
        if re.search(r'[A-Z]', password): charset_size += 26
        if re.search(r'[0-9]', password): charset_size += 10
        if re.search(r'[^a-zA-Z0-9]', password): charset_size += 32

        if charset_size == 0:
            return 0.0

        return len(password) * math.log2(charset_size)

    def build_charset(self, password_type: str, special_chars: str, exclude_chars: str, 
                     no_similar: bool, custom_charset: str = '') -> str:
        """Build character set based on password type and options."""
        charset = ''

        if password_type == 'strong':
            charset = self.lowercase + self.uppercase + self.digits + special_chars
        elif password_type == 'alpha':
            charset = self.lowercase + self.uppercase
        elif password_type == 'alphanum':
            charset = self.lowercase + self.uppercase + self.digits
        elif password_type == 'numeric':
            charset = self.digits
        elif password_type == 'custom':
            charset = custom_charset

        if exclude_chars:
            for char in exclude_chars:
                charset = charset.replace(char, '')

        if no_similar:
            for char in self.similar:
                charset = charset.replace(char, '')

        return charset

    def generate_passwords(self, length: int, count: int, password_type: str,
                          special_chars: str, exclude_chars: str, no_similar: bool,
                          min_upper: int, min_lower: int, min_digit: int, min_special: int,
                          custom_charset: str = '') -> List[str]:
        """Generate multiple passwords with specified requirements."""
        passwords = []
        attempts = 0

        # For pronounceable passwords and API keys, we don't use the charset validation
        if password_type not in ['pronounce', 'api-key']:
            charset = self.build_charset(password_type, special_chars, exclude_chars, 
                                       no_similar, custom_charset)
            if not charset:
                raise ValueError("Character set is empty after applying filters")

        while len(passwords) < count and attempts < self.max_attempts:
            attempts += 1

            if password_type == 'pronounce':
                password = self.generate_pronounceable_password(length)
            elif password_type == 'api-key':
                # For API keys, use the custom_charset as the format
                api_format = custom_charset if custom_charset else 'default'
                password = self.generate_api_key(length, api_format)
            else:
                charset = self.build_charset(password_type, special_chars, exclude_chars, 
                                           no_similar, custom_charset)
                password = self.generate_strong_password(length, charset)

            # Skip validation for API keys as they have their own format requirements
            if password_type == 'api-key' or self.validate_password(password, min_upper, min_lower, min_digit, min_special):
                passwords.append(password)

        if len(passwords) < count:
            raise RuntimeError(f"Could not generate {count} passwords meeting requirements after {self.max_attempts} attempts")

        return passwords

    def format_output(self, passwords: List[str], output_format: str, separator: str, key_names: Optional[List[str]] = None) -> str:
        """Format passwords according to specified output format."""
        if output_format == 'plain':
            if key_names:
                return '\n'.join([f"{name}: {pwd}" for name, pwd in zip(key_names, passwords)])
            return separator.join(passwords)
        elif output_format == 'json':
            if key_names:
                data = {name: pwd for name, pwd in zip(key_names, passwords)}
            else:
                data = [{"id": i + 1, "password": pwd} for i, pwd in enumerate(passwords)]
            return json.dumps(data, indent=2)
        elif output_format == 'csv':
            if key_names:
                lines = ['key,value']
                lines.extend([f'"{name}","{pwd}"' for name, pwd in zip(key_names, passwords)])
            else:
                lines = ['id,password']
                lines.extend([f'{i + 1},"{pwd}"' for i, pwd in enumerate(passwords)])
            return '\n'.join(lines)
        elif output_format == 'env':
            if key_names:
                lines = [f'{name}="{pwd}"' for name, pwd in zip(key_names, passwords)]
            else:
                lines = [f'PASSWORD_{i + 1}="{pwd}"' for i, pwd in enumerate(passwords)]
            return '\n'.join(lines)
        else:
            raise ValueError(f"Unknown output format: {output_format}")

    def get_analysis(self, password: str) -> Dict[str, any]:
        """Get comprehensive password analysis."""
        score, strength = self.calculate_strength(password)
        entropy = self.calculate_entropy(password)
        
        return {
            'password': password,
            'length': len(password),
            'strength': strength,
            'score': score,
            'max_score': 80,
            'entropy_bits': round(entropy, 2),
            'character_types': {
                'lowercase': bool(re.search(r'[a-z]', password)),
                'uppercase': bool(re.search(r'[A-Z]', password)),
                'digits': bool(re.search(r'[0-9]', password)),
                'special': bool(re.search(r'[^a-zA-Z0-9]', password))
            }
        }