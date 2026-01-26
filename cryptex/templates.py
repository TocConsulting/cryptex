"""
Password templates and policy definitions for compliance and standards.
"""

from typing import Dict, Any

# Predefined password policies
PASSWORD_TEMPLATES = {
    'nist-800-63b': {
        'length': 12,
        'min_upper': 1,
        'min_lower': 1,
        'min_digit': 1,
        'min_special': 1,
        'no_similar': True,
        'description': 'NIST 800-63B standard - US federal systems, enterprise compliance'
    },
    'pci-dss': {
        'length': 12,
        'min_upper': 1,
        'min_lower': 1,
        'min_digit': 1,
        'min_special': 1,
        'no_similar': False,
        'description': 'PCI DSS standard - Payment systems, credit card processing'
    },
    'owasp': {
        'length': 14,
        'min_upper': 2,
        'min_lower': 2,
        'min_digit': 2,
        'min_special': 2,
        'no_similar': True,
        'description': 'OWASP guidelines - Web applications, API authentication'
    },
    'high-security': {
        'length': 20,
        'min_upper': 3,
        'min_lower': 3,
        'min_digit': 3,
        'min_special': 3,
        'no_similar': True,
        'description': 'Maximum security - Admin accounts, root passwords, master keys'
    },
    'user-friendly': {
        'length': 12,
        'min_upper': 1,
        'min_lower': 1,
        'min_digit': 1,
        'min_special': 0,
        'no_similar': True,
        'exclude': '!@#$%^&*()_+-=[]{}|;:,.<>?',
        'description': 'Easy to type - End users, temporary accounts, shared devices'
    },
    'database': {
        'length': 16,
        'min_upper': 2,
        'min_lower': 2,
        'min_digit': 2,
        'min_special': 1,
        'exclude': '"\'\\`',
        'description': 'SQL-safe - Database connections, avoids quotes/backslashes'
    },
    'wifi': {
        'length': 16,
        'min_upper': 2,
        'min_lower': 2,
        'min_digit': 2,
        'min_special': 0,
        'no_similar': True,
        'exclude': '!@#$%^&*()_+-=[]{}|;:,.<>?',
        'description': 'WiFi networks - Easy to type on phones, no special characters'
    }
}


def get_template(template_name: str) -> Dict[str, Any]:
    """Get password template by name."""
    if template_name not in PASSWORD_TEMPLATES:
        available = ', '.join(PASSWORD_TEMPLATES.keys())
        raise ValueError(f"Unknown template '{template_name}'. Available: {available}")
    
    return PASSWORD_TEMPLATES[template_name].copy()


def list_templates() -> Dict[str, str]:
    """List all available templates with descriptions."""
    return {name: template['description'] for name, template in PASSWORD_TEMPLATES.items()}


def get_template_details() -> Dict[str, Dict[str, Any]]:
    """Get all templates with full details."""
    return PASSWORD_TEMPLATES.copy()


def apply_template(template_name: str) -> Dict[str, Any]:
    """Apply template and return the configuration."""
    template = get_template(template_name)
    
    # Remove description from the config
    config = {k: v for k, v in template.items() if k != 'description'}
    
    return config