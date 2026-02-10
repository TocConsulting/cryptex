"""
Command-line interface for Cryptex password generator.
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

import click

from .generator import PasswordGenerator
from .integrations import AWSSecretsManager, OSKeychain, HashiCorpVault
from .templates import apply_template, list_templates as get_templates, get_template_details
from .utils import (
    check_dependencies,
    compute_totp_code,
    copy_to_clipboard,
    decode_qr_image,
    format_analysis_output,
    generate_qr_code,
    generate_totp_qr_code,
    parse_otpauth_uri,
    print_colored,
    print_error,
    print_success,
    print_warning,
    validate_count,
    validate_length,
    validate_min_requirements,
)


@click.command()
@click.option(
    '-l', '--length',
    default=16,
    callback=validate_length,
    help='Password length (8-256)',
    show_default=True
)
@click.option(
    '-c', '--count',
    default=1,
    callback=validate_count,
    help='Number of passwords to generate',
    show_default=True
)
@click.option(
    '-t', '--type',
    'password_type',
    type=click.Choice(['strong', 'alpha', 'alphanum', 'numeric', 'pronounce', 'custom', 'api-key']),
    default='strong',
    help='Password type',
    show_default=True
)
@click.option(
    '-s', '--special',
    default='!@#$%^&*()_+-=[]{}|;:,.<>?',
    help='Custom special characters',
    show_default=True
)
@click.option(
    '-x', '--exclude',
    default='',
    help='Exclude specific characters'
)
@click.option(
    '--no-similar',
    is_flag=True,
    help='Exclude similar looking characters (il1Lo0O)'
)
@click.option(
    '--min-upper',
    default=0,
    callback=validate_min_requirements,
    help='Minimum uppercase letters',
    show_default=True
)
@click.option(
    '--min-lower',
    default=0,
    callback=validate_min_requirements,
    help='Minimum lowercase letters',
    show_default=True
)
@click.option(
    '--min-digit',
    default=0,
    callback=validate_min_requirements,
    help='Minimum digits',
    show_default=True
)
@click.option(
    '--min-special',
    default=0,
    callback=validate_min_requirements,
    help='Minimum special characters',
    show_default=True
)
@click.option(
    '-f', '--format',
    'output_format',
    type=click.Choice(['plain', 'json', 'csv', 'env']),
    default='plain',
    help='Output format',
    show_default=True
)
@click.option(
    '--separator',
    default='\n',
    help='Separator for multiple passwords',
    show_default=True
)
@click.option(
    '--copy',
    is_flag=True,
    help='Copy to clipboard (requires pbcopy/xclip)'
)
@click.option(
    '--qr',
    is_flag=True,
    help='Generate QR code of password (for sharing WiFi passwords, etc.)'
)
@click.option(
    '--totp',
    is_flag=True,
    help='Generate TOTP secret for 2FA apps (Google Authenticator, Authy)'
)
@click.option(
    '--totp-issuer',
    default='Cryptex',
    help='Issuer name shown in 2FA app (e.g., company name)',
    show_default=True
)
@click.option(
    '--totp-account',
    help='Account name shown in 2FA app (e.g., user@example.com)'
)
@click.option(
    '--totp-code',
    default=None,
    help='Read TOTP code from a base32 secret or QR code image path'
)
@click.option(
    '-q', '--quiet',
    is_flag=True,
    help='Suppress all output except passwords'
)
@click.option(
    '-v', '--verbose',
    is_flag=True,
    help='Show password strength analysis'
)
@click.option(
    '--custom-charset',
    default='',
    help='Custom character set (use with --type custom)'
)
@click.option(
    '--api-format',
    type=click.Choice(['uuid', 'uuid-hex', 'base64', 'hex', 'url-safe', 'alphanum']),
    default='alphanum',
    help='API key format (use with --type api-key)',
    show_default=True
)
@click.option(
    '--kv',
    '--key-value',
    help='Generate key-value pairs (comma-separated names): DATABASE_PASSWORD,API_KEY,JWT_SECRET'
)
@click.option(
    '--save-aws',
    is_flag=True,
    help='Save to AWS Secrets Manager (requires AWS credentials)'
)
@click.option(
    '--aws-secret-name',
    help='AWS secret name (required with --save-aws)'
)
@click.option(
    '--aws-region',
    default='us-east-1',
    help='AWS region',
    show_default=True
)
@click.option(
    '--aws-profile',
    help='AWS profile name (from ~/.aws/credentials). If not specified, uses environment variables or default profile'
)
@click.option(
    '--save-keychain',
    is_flag=True,
    help='Save to OS keychain (macOS/Linux/Windows)'
)
@click.option(
    '--keychain-service',
    default='cryptex',
    help='Keychain service name',
    show_default=True
)
@click.option(
    '--keychain-account',
    help='Keychain account name (required with --save-keychain for single passwords)'
)
@click.option(
    '--template',
    type=click.Choice(['nist-800-63b', 'pci-dss', 'owasp', 'high-security', 'user-friendly', 'database', 'wifi']),
    help='Use predefined password template/policy'
)
@click.option(
    '--list-templates',
    is_flag=True,
    help='List available password templates and exit'
)
@click.option(
    '--save-vault',
    is_flag=True,
    help='Save to HashiCorp Vault (requires vault setup)'
)
@click.option(
    '--vault-path',
    help='Vault path (required with --save-vault)'
)
@click.option(
    '--vault-url',
    default='http://localhost:8200',
    help='Vault URL',
    show_default=True
)
@click.argument(
    'output_file',
    type=click.Path(),
    required=False
)
@click.version_option(version='1.1.0', prog_name='cryptex')
def main(
    length: int,
    count: int,
    password_type: str,
    special: str,
    exclude: str,
    no_similar: bool,
    min_upper: int,
    min_lower: int,
    min_digit: int,
    min_special: int,
    output_format: str,
    separator: str,
    copy: bool,
    qr: bool,
    totp: bool,
    totp_issuer: str,
    totp_account: Optional[str],
    totp_code: Optional[str],
    quiet: bool,
    verbose: bool,
    custom_charset: str,
    api_format: str,
    kv: Optional[str],
    save_aws: bool,
    aws_secret_name: Optional[str],
    aws_region: str,
    aws_profile: Optional[str],
    save_keychain: bool,
    keychain_service: str,
    keychain_account: Optional[str],
    template: Optional[str],
    list_templates: bool,
    save_vault: bool,
    vault_path: Optional[str],
    vault_url: str,
    output_file: Optional[str]
):
    """
    Cryptex - Enterprise Password Generator

    Generate cryptographically secure passwords, API keys, and TOTP secrets.

    \b
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    QUICK START
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    \b
      cryptex                      Generate a 16-char secure password
      cryptex -l 24                Generate a 24-char password
      cryptex --template owasp     Use OWASP security standard
      cryptex --list-templates     See all compliance templates

    \b
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    PASSWORD TYPES (-t, --type)
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    \b
      strong     Letters + numbers + symbols (default)
      alpha      Letters only (A-Z, a-z)
      alphanum   Letters + numbers
      numeric    Numbers only (PINs)
      pronounce  Easy to read aloud: "KaLoMi72"
      api-key    API keys (use with --api-format)

    \b
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    2FA / TOTP (Google Authenticator, Authy)
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    \b
      cryptex --totp --totp-issuer "GitHub" --totp-account "user@email.com"

      Generates a TOTP secret + QR code you can scan with Google Authenticator.
      The issuer and account appear in your 2FA app to identify the entry.

    \b
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    TOTP CODE READER (get current 6-digit code)
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    \b
      cryptex --totp-code "JBSWY3DPEHPK3PXP"
      cryptex --totp-code ./qr-code.png
      cryptex --totp-code "JBSWY3DPEHPK3PXP" --copy
      cryptex --totp-code "JBSWY3DPEHPK3PXP" -q

      Provide a base32 secret or a QR code image to get the current TOTP code.

    \b
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    QR CODE (for WiFi, password sharing)
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    \b
      cryptex --template wifi --qr     WiFi password with scannable QR

      The --qr flag shows the password as QR code for easy sharing.
      Note: This is NOT for 2FA apps. Use --totp for Google Authenticator.

    \b
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    COMPLIANCE TEMPLATES (--template, --list-templates)
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    \b
      cryptex --list-templates         Show all templates with details
      cryptex --template nist-800-63b  NIST standard (12 chars, mixed)
      cryptex --template pci-dss       Payment card industry standard
      cryptex --template high-security Admin accounts (20+ chars)

    \b
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    DEVOPS & AUTOMATION
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    \b
      # Generate .env file with multiple secrets
      cryptex --kv "DB_PASS,API_KEY,JWT_SECRET" -f env > .env

      # Save to AWS Secrets Manager
      cryptex -l 32 --save-aws --aws-secret-name "prod/db-password"

      # Save to HashiCorp Vault
      cryptex --save-vault --vault-path "secret/myapp/api-key"

      # Save to OS keychain (macOS/Linux/Windows)
      cryptex --save-keychain --keychain-service MyApp --keychain-account admin
    """
    
    # Handle list templates
    if list_templates:
        print_colored("Available Compliance Templates", color='green', bold=True)
        click.echo()

        for name, details in get_template_details().items():
            print_colored(f"  {name}", color='cyan', bold=True)
            click.echo(f"    {details['description']}")
            click.echo(f"    Length: {details['length']} chars | ", nl=False)

            reqs = []
            if details.get('min_upper', 0) > 0:
                reqs.append(f"{details['min_upper']}+ uppercase")
            if details.get('min_lower', 0) > 0:
                reqs.append(f"{details['min_lower']}+ lowercase")
            if details.get('min_digit', 0) > 0:
                reqs.append(f"{details['min_digit']}+ digits")
            if details.get('min_special', 0) > 0:
                reqs.append(f"{details['min_special']}+ special")

            if reqs:
                click.echo(f"Requirements: {', '.join(reqs)}")
            else:
                click.echo("Requirements: flexible")

            if details.get('no_similar'):
                click.echo("    Excludes similar characters (i, l, 1, L, o, 0, O)")

            click.echo(f"    Usage: cryptex --template {name}")
            click.echo()

        sys.exit(0)
    
    # Check dependencies early
    dep_error = check_dependencies(copy)
    if dep_error:
        print_error(dep_error)
        sys.exit(1)
    
    # Validate custom charset requirement
    if password_type == 'custom' and not custom_charset:
        print_error("Custom charset must be provided when using --type custom")
        sys.exit(1)
    
    # Apply template if specified
    if template:
        template_config = apply_template(template)
        # Override with template values
        length = template_config.get('length', length)
        min_upper = template_config.get('min_upper', min_upper)
        min_lower = template_config.get('min_lower', min_lower)
        min_digit = template_config.get('min_digit', min_digit)
        min_special = template_config.get('min_special', min_special)
        no_similar = template_config.get('no_similar', no_similar)
        if 'exclude' in template_config:
            exclude = template_config['exclude']
    
    # For API keys, use api_format as custom_charset
    if password_type == 'api-key':
        custom_charset = api_format
    
    # Handle key-value pairs
    key_names = None
    if kv:
        key_names = [name.strip() for name in kv.split(',')]
        count = len(key_names)  # Override count with number of keys
    
    # Validate AWS options
    if save_aws and not aws_secret_name:
        print_error("--aws-secret-name is required when using --save-aws")
        sys.exit(1)
    
    # Validate keychain options
    if save_keychain and not kv and not keychain_account and not totp_code and not totp:
        print_error("--keychain-account is required when using --save-keychain for single passwords")
        sys.exit(1)
    
    # Validate vault options
    if save_vault and not vault_path:
        print_error("--vault-path is required when using --save-vault")
        sys.exit(1)

    # Validate TOTP options
    if totp and not totp_account:
        print_error("--totp-account is required when using --totp (e.g., --totp-account user@example.com)")
        sys.exit(1)

    # TOTP mode is a special flow - generate and display TOTP secret
    if totp:
        if not quiet:
            print_colored("Cryptex - TOTP Secret Generator", color='green', bold=True)
            click.echo()
            print_colored(f"Issuer:  {totp_issuer}", color='cyan')
            print_colored(f"Account: {totp_account}", color='cyan')
            click.echo()

        # Generate TOTP secret and display QR code
        totp_result = generate_totp_qr_code(totp_issuer, totp_account, quiet=quiet)

        if totp_result:
            if not quiet:
                print_success("Scan the QR code above with Google Authenticator, Authy, or any TOTP app")
                click.echo()
                print_colored("Manual entry (if QR scan fails):", color='yellow')
                click.echo(f"  Secret: {totp_result['secret']}")
                click.echo(f"  Type: Time-based (TOTP)")
                click.echo(f"  Algorithm: SHA1")
                click.echo(f"  Digits: 6")
                click.echo(f"  Period: 30 seconds")

            # Handle storage integrations for TOTP
            if save_keychain:
                try:
                    keychain = OSKeychain()
                    success = keychain.save_secret(keychain_service, totp_account, totp_result['secret'])
                    if success and not quiet:
                        print_success(f"TOTP secret saved to keychain: {keychain_service}/{totp_account}")
                except Exception as e:
                    print_error(f"Failed to save to keychain: {e}")

            if output_file:
                output_path = Path(output_file)
                output_path.write_text(json.dumps({
                    'issuer': totp_issuer,
                    'account': totp_account,
                    'secret': totp_result['secret'],
                    'uri': totp_result['uri']
                }, indent=2))
                if not quiet:
                    print_success(f"TOTP details saved to {output_file}")
        else:
            print_error("Failed to generate TOTP. The qrcode library may not be installed properly.")
            sys.exit(1)

        sys.exit(0)

    # TOTP code reader mode - compute TOTP code from secret or QR image
    if totp_code:
        secret = None
        issuer = None
        account = None

        # Smart detection: file path vs. base32 secret
        if os.path.isfile(totp_code):
            decoded = decode_qr_image(totp_code)
            if decoded is None:
                print_error(f"Could not decode QR code from image: {totp_code}")
                sys.exit(1)

            try:
                totp_params = parse_otpauth_uri(decoded)
                secret = totp_params['secret']
                issuer = totp_params.get('issuer', '')
                account = totp_params.get('account', '')
            except ValueError as e:
                print_error(str(e))
                sys.exit(1)
        else:
            secret = totp_code

        # Compute current and next TOTP codes
        try:
            current = compute_totp_code(secret, offset=0)
            next_code = compute_totp_code(secret, offset=1)
        except ValueError as e:
            print_error(str(e))
            sys.exit(1)

        if quiet:
            click.echo(current['code'])
        else:
            print_colored("Cryptex - TOTP Code Reader", color='green', bold=True)
            click.echo()

            if issuer or account:
                if issuer:
                    print_colored(f"Issuer:  {issuer}", color='cyan')
                if account:
                    print_colored(f"Account: {account}", color='cyan')
                click.echo()

            print_colored(f"TOTP Code: {current['code']}", color='cyan', bold=True)

            remaining = current['remaining']
            if remaining >= 10:
                time_color = 'green'
            elif remaining >= 5:
                time_color = 'yellow'
            else:
                time_color = 'red'
            print_colored(f"Valid for: {remaining} seconds", color=time_color)

            print_colored(f"Next code: {next_code['code']}", color='blue')

        # Handle clipboard copy
        if copy:
            if copy_to_clipboard(current['code']):
                if not quiet:
                    print_success("TOTP code copied to clipboard!")
            else:
                print_error("Failed to copy to clipboard. Ensure pbcopy (macOS) or xclip (Linux) is installed.")
                sys.exit(1)

        # Handle keychain save (save the secret, not the ephemeral code)
        if save_keychain:
            keychain_acct = account or keychain_account or 'totp-secret'
            try:
                keychain = OSKeychain()
                success = keychain.save_secret(keychain_service, keychain_acct, secret)
                if success and not quiet:
                    print_success(f"TOTP secret saved to keychain: {keychain_service}/{keychain_acct}")
            except Exception as e:
                print_error(f"Failed to save to keychain: {e}")

        sys.exit(0)

    # Show banner unless quiet
    if not quiet:
        print_colored("Cryptex - Enhanced Random Password Generator", color='green', bold=True)
        click.echo()
    
    # Initialize generator
    generator = PasswordGenerator()
    
    try:
        # Generate passwords
        passwords = generator.generate_passwords(
            length=length,
            count=count,
            password_type=password_type,
            special_chars=special,
            exclude_chars=exclude,
            no_similar=no_similar,
            min_upper=min_upper,
            min_lower=min_lower,
            min_digit=min_digit,
            min_special=min_special,
            custom_charset=custom_charset
        )
        
        # Format output
        output = generator.format_output(passwords, output_format, separator, key_names)
        
        # Handle output
        if output_file:
            output_path = Path(output_file)
            output_path.write_text(output)
            if not quiet:
                print_success(f"Password(s) saved to {output_file}")
        else:
            # Always output passwords (quiet mode only suppresses banner/messages)
            click.echo(output)
        
        # Show analysis if verbose
        if verbose and not quiet:
            for password in passwords:
                analysis = generator.get_analysis(password)
                click.echo(format_analysis_output(analysis))
        
        # Handle clipboard copy
        if copy:
            if len(passwords) > 1:
                print_warning("Multiple passwords generated. Only the first will be copied to clipboard.")
            
            if copy_to_clipboard(passwords[0]):
                if not quiet:
                    print_success("Password copied to clipboard!")
            else:
                print_error("Failed to copy to clipboard. Ensure pbcopy (macOS) or xclip (Linux) is installed.")
                sys.exit(1)
        
        # Handle QR code generation
        if qr:
            if len(passwords) > 1:
                print_warning("Multiple passwords generated. Only showing QR code for the first.")
            
            if not quiet:
                print_colored("\nQR Code:", color='blue', bold=True)
            
            if not generate_qr_code(passwords[0]):
                print_error("Failed to generate QR code. The qrcode library may not be installed properly.")
                sys.exit(1)
        
        # Handle AWS Secrets Manager integration
        if save_aws:
            try:
                aws_manager = AWSSecretsManager(region_name=aws_region, profile_name=aws_profile)
                
                if key_names and len(passwords) > 1:
                    # Save as key-value pairs in a single secret
                    secrets_dict = {name: pwd for name, pwd in zip(key_names, passwords)}
                    success = aws_manager.save_secret(aws_secret_name, json.dumps(secrets_dict))
                    if success:
                        if not quiet:
                            print_success(f"Secrets saved to AWS Secrets Manager: {aws_secret_name}")
                    else:
                        print_error("Failed to save secrets to AWS Secrets Manager")
                        sys.exit(1)
                else:
                    # Save single password
                    success = aws_manager.save_secret(aws_secret_name, passwords[0])
                    if success:
                        if not quiet:
                            print_success(f"Secret saved to AWS Secrets Manager: {aws_secret_name}")
                    else:
                        print_error("Failed to save secret to AWS Secrets Manager")
                        sys.exit(1)
            
            except (ImportError, ValueError) as e:
                print_error(f"AWS integration error: {e}")
                sys.exit(1)
        
        # Handle OS Keychain integration
        if save_keychain:
            try:
                keychain = OSKeychain()
                
                if key_names and len(passwords) > 1:
                    # Save multiple passwords with key names
                    secrets_dict = {name: pwd for name, pwd in zip(key_names, passwords)}
                    results = keychain.save_multiple_secrets(keychain_service, secrets_dict)
                    
                    success_count = sum(results.values())
                    if success_count == len(passwords):
                        if not quiet:
                            print_success(f"All {len(passwords)} secrets saved to OS keychain")
                    else:
                        print_error(f"Only {success_count}/{len(passwords)} secrets saved to keychain")
                        sys.exit(1)
                else:
                    # Save single password
                    success = keychain.save_secret(keychain_service, keychain_account, passwords[0])
                    if success:
                        if not quiet:
                            print_success(f"Secret saved to OS keychain: {keychain_service}/{keychain_account}")
                    else:
                        print_error("Failed to save secret to OS keychain")
                        sys.exit(1)
            
            except (ImportError, ValueError) as e:
                print_error(f"Keychain integration error: {e}")
                sys.exit(1)
        
        # Handle HashiCorp Vault integration
        if save_vault:
            try:
                # Get Vault token from environment
                vault_token = os.getenv('VAULT_TOKEN')
                
                if not vault_token:
                    print_error("VAULT_TOKEN environment variable not set. Please set it with: export VAULT_TOKEN=your-token")
                    sys.exit(1)
                
                vault_manager = HashiCorpVault(url=vault_url, token=vault_token)
                
                if key_names and len(passwords) > 1:
                    # Save as key-value pairs in a single vault path
                    secrets_dict = {name: pwd for name, pwd in zip(key_names, passwords)}
                    success = vault_manager.save_multiple_secrets(vault_path, secrets_dict)
                    if success:
                        if not quiet:
                            print_success(f"Secrets saved to Vault: {vault_path}")
                    else:
                        print_error("Failed to save secrets to Vault")
                        sys.exit(1)
                else:
                    # Save single password
                    success = vault_manager.save_secret(vault_path, passwords[0])
                    if success:
                        if not quiet:
                            print_success(f"Secret saved to Vault: {vault_path}")
                    else:
                        print_error("Failed to save secret to Vault")
                        sys.exit(1)
            
            except (ImportError, ValueError) as e:
                print_error(f"Vault integration error: {e}")
                sys.exit(1)
    
    except (ValueError, RuntimeError) as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        print_error("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()