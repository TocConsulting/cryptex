"""
Utility functions for clipboard, QR code generation, and system integration.
"""

import base64
import hashlib
import hmac
import io
import secrets
import shutil
import struct
import subprocess
import sys
import time as time_module
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, quote, unquote, urlparse

import click
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode as pyzbar_decode


class Colors:
    """ANSI color codes for terminal output."""
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'


def copy_to_clipboard(password: str) -> bool:
    """Copy password to clipboard if possible."""
    try:
        if shutil.which('pbcopy'):  # macOS
            subprocess.run(['pbcopy'], input=password.encode(), check=True)
            return True
        elif shutil.which('xclip'):  # Linux
            subprocess.run(['xclip', '-selection', 'clipboard'], 
                         input=password.encode(), check=True)
            return True
    except subprocess.CalledProcessError:
        pass
    return False


def generate_qr_code(password: str) -> bool:
    """Generate QR code for password using native Python library."""
    try:
        qr = qrcode.QRCode(border=1)
        qr.add_data(password)
        qr.make(fit=True)

        # Print ASCII representation to terminal
        f = io.StringIO()
        qr.print_ascii(out=f)
        f.seek(0)
        click.echo(f.read())
        return True
    except Exception:
        return False


def generate_totp_qr_code(issuer: str, account: str, quiet: bool = False) -> Optional[Dict[str, str]]:
    """
    Generate a TOTP secret and QR code for Google Authenticator / Authy.

    Returns dict with 'secret' and 'uri' on success, None on failure.
    """
    try:
        # Generate 20 bytes (160 bits) of random data for TOTP secret
        secret_bytes = secrets.token_bytes(20)
        # Encode as base32 (standard for TOTP, no padding)
        secret = base64.b32encode(secret_bytes).decode('ascii').rstrip('=')

        # Build otpauth URI for TOTP
        # Format: otpauth://totp/ISSUER:ACCOUNT?secret=SECRET&issuer=ISSUER
        label = f"{issuer}:{account}"
        uri = f"otpauth://totp/{quote(label)}?secret={secret}&issuer={quote(issuer)}"

        if not quiet:
            # Generate and display QR code
            qr = qrcode.QRCode(border=1)
            qr.add_data(uri)
            qr.make(fit=True)

            f = io.StringIO()
            qr.print_ascii(out=f)
            f.seek(0)
            click.echo(f.read())

        return {'secret': secret, 'uri': uri}
    except Exception:
        return None


def compute_totp_code(secret: str, time_step: int = 30, digits: int = 6,
                      algorithm: str = 'sha1', offset: int = 0) -> Dict[str, Any]:
    """
    Compute a TOTP code from a base32 secret per RFC 6238.

    Args:
        secret: Base32-encoded TOTP secret (with or without padding).
        time_step: Time step in seconds (default 30).
        digits: Number of digits in the code (default 6).
        algorithm: Hash algorithm (default 'sha1').
        offset: Number of time steps to offset (0 = current, 1 = next).

    Returns:
        Dict with 'code' (str), 'remaining' (int seconds), 'period' (int).
    """
    # Normalize the secret: uppercase, strip spaces/dashes, re-pad to multiple of 8
    clean_secret = secret.upper().replace(' ', '').replace('-', '')
    padding = (8 - len(clean_secret) % 8) % 8
    clean_secret += '=' * padding

    try:
        key = base64.b32decode(clean_secret)
    except Exception:
        raise ValueError(f"Invalid base32 TOTP secret: '{secret}'")

    # Current time counter
    now = int(time_module.time())
    counter = (now // time_step) + offset
    remaining = time_step - (now % time_step)

    # HMAC computation (RFC 4226 / RFC 6238)
    hash_name = algorithm.lower()
    counter_bytes = struct.pack('>Q', counter)
    mac = hmac.new(key, counter_bytes, getattr(hashlib, hash_name)).digest()

    # Dynamic truncation
    offset_byte = mac[-1] & 0x0F
    truncated = struct.unpack('>I', mac[offset_byte:offset_byte + 4])[0] & 0x7FFFFFFF
    code = str(truncated % (10 ** digits)).zfill(digits)

    return {
        'code': code,
        'remaining': remaining,
        'period': time_step,
    }


def decode_qr_image(image_path: str) -> Optional[str]:
    """Decode a QR code image and return its text content."""
    try:
        image = Image.open(image_path)
        decoded_objects = pyzbar_decode(image)
        if decoded_objects:
            return decoded_objects[0].data.decode('utf-8')
        return None
    except Exception:
        return None


def parse_otpauth_uri(uri: str) -> Dict[str, Any]:
    """
    Parse an otpauth:// URI and extract TOTP parameters.

    Returns dict with 'secret', 'issuer', 'account', 'algorithm', 'digits', 'period'.
    """
    parsed = urlparse(uri)
    if parsed.scheme != 'otpauth' or parsed.netloc != 'totp':
        raise ValueError(f"Not a valid otpauth TOTP URI: {uri}")

    # Label is the path component (e.g., /Issuer:account)
    label = unquote(parsed.path.lstrip('/'))
    params = parse_qs(parsed.query)

    secret = params.get('secret', [None])[0]
    if not secret:
        raise ValueError("No secret found in otpauth URI")

    issuer = params.get('issuer', [''])[0]
    account = label
    if ':' in label:
        issuer_from_label, account = label.split(':', 1)
        if not issuer:
            issuer = issuer_from_label

    return {
        'secret': secret,
        'issuer': issuer,
        'account': account,
        'algorithm': params.get('algorithm', ['SHA1'])[0],
        'digits': int(params.get('digits', ['6'])[0]),
        'period': int(params.get('period', ['30'])[0]),
    }


def check_dependencies(copy_enabled: bool) -> Optional[str]:
    """Check if required dependencies are available."""
    missing = []

    if copy_enabled:
        if not (shutil.which('pbcopy') or shutil.which('xclip')):
            missing.append("pbcopy (macOS) or xclip (Linux) for clipboard support")
    
    if missing:
        return f"Missing dependencies: {', '.join(missing)}"
    
    return None


def print_colored(text: str, color: str = '', bold: bool = False, file=None) -> None:
    """Print colored text to terminal."""
    if file is None:
        file = sys.stdout
    
    prefix = ''
    if bold:
        prefix += Colors.BOLD
    if color:
        prefix += getattr(Colors, color.upper(), '')
    
    suffix = Colors.RESET if prefix else ''
    
    click.echo(f"{prefix}{text}{suffix}", file=file)


def print_error(message: str) -> None:
    """Print error message and exit."""
    print_colored(f"Error: {message}", color='red', bold=True, file=sys.stderr)


def print_success(message: str) -> None:
    """Print success message."""
    print_colored(message, color='green', bold=True)


def print_warning(message: str) -> None:
    """Print warning message."""
    print_colored(f"Warning: {message}", color='yellow', bold=True, file=sys.stderr)


def format_analysis_output(analysis: dict) -> str:
    """Format password analysis for display."""
    strength_colors = {
        'Very Strong': 'green',
        'Strong': 'green',
        'Moderate': 'yellow',
        'Weak': 'red'
    }
    
    strength_color = strength_colors.get(analysis['strength'], 'white')
    
    output = []
    output.append(f"\n{Colors.BOLD}{Colors.BLUE}Password Analysis:{Colors.RESET}")
    output.append(f"\nPassword: {Colors.BOLD}{analysis['password']}{Colors.RESET}")
    
    strength_colored = f"{Colors.BOLD}{getattr(Colors, strength_color.upper())}{analysis['strength']}{Colors.RESET}"
    output.append(f"Strength: {strength_colored} (Score: {analysis['score']}/{analysis['max_score']})")
    output.append(f"Entropy: {analysis['entropy_bits']} bits")
    output.append(f"Length: {analysis['length']} characters")
    
    char_types = []
    if analysis['character_types']['lowercase']:
        char_types.append("lowercase")
    if analysis['character_types']['uppercase']:
        char_types.append("uppercase")
    if analysis['character_types']['digits']:
        char_types.append("digits")
    if analysis['character_types']['special']:
        char_types.append("special")
    
    output.append(f"Character types: {', '.join(char_types)}")
    
    return '\n'.join(output)


def validate_length(ctx, param, value):
    """Validate password length parameter."""
    if value < 8 or value > 256:
        raise click.BadParameter('Length must be between 8 and 256')
    return value


def validate_count(ctx, param, value):
    """Validate count parameter."""
    if value < 1:
        raise click.BadParameter('Count must be at least 1')
    return value


def validate_min_requirements(ctx, param, value):
    """Validate minimum character requirements."""
    if value < 0:
        raise click.BadParameter('Minimum requirements cannot be negative')
    return value