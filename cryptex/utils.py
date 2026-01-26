"""
Utility functions for clipboard, QR code generation, and system integration.
"""

import base64
import io
import secrets
import shutil
import subprocess
import sys
from typing import Dict, Optional
from urllib.parse import quote

import click
try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False


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
    if not HAS_QRCODE:
        return False

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
    if not HAS_QRCODE:
        return None

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


def check_dependencies(copy_enabled: bool, qr_enabled: bool) -> Optional[str]:
    """Check if required dependencies are available."""
    missing = []
    
    if copy_enabled:
        if not (shutil.which('pbcopy') or shutil.which('xclip')):
            missing.append("pbcopy (macOS) or xclip (Linux) for clipboard support")
    
    if qr_enabled and not HAS_QRCODE:
        missing.append("qrcode Python library for QR code generation (install with: pip install qrcode)")
    
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