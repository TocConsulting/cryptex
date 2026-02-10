# Cryptex Usage Guide

Complete guide to every Cryptex command with real-world use cases.

---

## Table of Contents

1. [Basic Password Generation](#basic-password-generation)
2. [Password Length](#password-length)
3. [Password Types](#password-types)
4. [Character Requirements](#character-requirements)
5. [Character Exclusions](#character-exclusions)
6. [Compliance Templates](#compliance-templates)
7. [API Key Generation](#api-key-generation)
8. [TOTP / 2FA Generation](#totp--2fa-generation)
9. [TOTP Code Reader](#totp-code-reader)
10. [QR Code Generation](#qr-code-generation)
11. [Key-Value Pairs](#key-value-pairs)
12. [Output Formats](#output-formats)
13. [Clipboard Integration](#clipboard-integration)
14. [Password Analysis](#password-analysis)
15. [Storage Integrations](#storage-integrations)
16. [Quiet Mode](#quiet-mode)

---

## Basic Password Generation

### Command
```bash
cryptex
```

### What it does
Generates a single 16-character password with uppercase, lowercase, numbers, and special characters.

### Use cases
- Quick password generation for any account
- When you need a secure password immediately
- General-purpose password needs

### Example output
```
Cryptex - Enhanced Random Password Generator

xK9#mL2$vN7@pQ5!
```

---

## Password Length

### Command
```bash
cryptex -l <length>
cryptex --length <length>
```

### What it does
Sets the password length (minimum 8, maximum 256 characters).

### Use cases

| Length | Use Case |
|--------|----------|
| `-l 8` | Minimum security, legacy systems with length limits |
| `-l 12` | Standard accounts, email, social media |
| `-l 16` | Default, good for most applications |
| `-l 20` | Sensitive accounts, banking, financial |
| `-l 24` | Administrative accounts, server access |
| `-l 32` | API keys, encryption keys, master passwords |
| `-l 64` | Maximum security, long-term secrets |

### Examples
```bash
# Short password for a legacy system
cryptex -l 8

# Long password for admin account
cryptex -l 24

# Very long password for master key
cryptex -l 64
```

---

## Password Types

### Command
```bash
cryptex -t <type>
cryptex --type <type>
```

### Available types and use cases

#### `strong` (default)
```bash
cryptex -t strong
```
- **Characters**: A-Z, a-z, 0-9, special symbols
- **Use cases**:
  - Most secure option for any account
  - Web applications, email, banking
  - Any system that accepts special characters

#### `alpha`
```bash
cryptex -t alpha
```
- **Characters**: A-Z, a-z only
- **Use cases**:
  - Systems that don't accept numbers or symbols
  - Some older enterprise systems
  - Certain API restrictions
  - When you need letters only

#### `alphanum`
```bash
cryptex -t alphanum
```
- **Characters**: A-Z, a-z, 0-9
- **Use cases**:
  - Systems that don't accept special characters
  - URL-safe identifiers
  - File names that need to be passwords
  - Some database systems

#### `numeric`
```bash
cryptex -t numeric
```
- **Characters**: 0-9 only
- **Use cases**:
  - PIN codes for phones, bank cards
  - Numeric-only authentication systems
  - Door codes, safe combinations
  - Voicemail passwords

```bash
# Generate a 6-digit PIN
cryptex -t numeric -l 8
```

#### `pronounce`
```bash
cryptex -t pronounce
```
- **Characters**: Alternating consonants and vowels + numbers
- **Use cases**:
  - Passwords you need to read aloud (phone support)
  - Temporary passwords for users
  - Shared passwords in meetings
  - When memorability matters

```bash
# Easy to read aloud: "KaLoMi72BeXu"
cryptex -t pronounce -l 12
```

#### `custom`
```bash
cryptex -t custom --custom-charset "ABC123"
```
- **Characters**: Only what you specify
- **Use cases**:
  - Specific character requirements
  - Restricted character sets
  - Special encoding needs

```bash
# Hexadecimal password
cryptex -t custom --custom-charset "0123456789ABCDEF" -l 16

# Only specific characters allowed by a system
cryptex -t custom --custom-charset "abcdefghjkmnpqrstuvwxyz23456789" -l 12
```

---

## Character Requirements

### Commands
```bash
cryptex --min-upper <n>      # Minimum uppercase letters
cryptex --min-lower <n>      # Minimum lowercase letters
cryptex --min-digit <n>      # Minimum digits
cryptex --min-special <n>    # Minimum special characters
```

### Use cases
- Meeting specific password policies
- Corporate security requirements
- Compliance with system rules

### Examples
```bash
# Corporate policy: at least 2 uppercase, 2 digits, 1 special
cryptex -l 16 --min-upper 2 --min-digit 2 --min-special 1

# Bank requirement: at least 3 of each type
cryptex -l 20 --min-upper 3 --min-lower 3 --min-digit 3 --min-special 3
```

---

## Character Exclusions

### Commands
```bash
cryptex -x "<chars>"         # Exclude specific characters
cryptex --exclude "<chars>"
cryptex --no-similar         # Exclude similar-looking characters
```

### Use cases for `--exclude`

| Exclude | Reason |
|---------|--------|
| `-x "0O"` | Avoid confusion between zero and letter O |
| `-x "1lI"` | Avoid confusion between one, lowercase L, uppercase I |
| `-x "'\"\`"` | Database/SQL safety |
| `-x "@"` | Email field confusion |
| `-x "&<>"` | HTML/XML safety |

### Use cases for `--no-similar`
```bash
cryptex --no-similar
```
Excludes: `i, l, 1, L, o, 0, O`

- Passwords that will be read visually
- Handwritten password sharing
- Reducing user input errors
- Phone support scenarios

### Examples
```bash
# Avoid SQL injection characters
cryptex -l 20 -x "'\"\`;\\"

# Easy to read, no confusing characters
cryptex -l 16 --no-similar

# Combine both
cryptex -l 16 --no-similar -x "@#"
```

---

## Compliance Templates

### Command
```bash
cryptex --template <name>
cryptex --list-templates      # Show all templates
```

### Available templates

#### `nist-800-63b`
```bash
cryptex --template nist-800-63b
```
- **Standard**: NIST Special Publication 800-63B
- **Use cases**:
  - US federal government systems
  - Government contractors
  - Enterprise compliance requirements
  - When auditors require NIST compliance

#### `pci-dss`
```bash
cryptex --template pci-dss
```
- **Standard**: Payment Card Industry Data Security Standard
- **Use cases**:
  - E-commerce platforms
  - Payment processing systems
  - Credit card handling applications
  - Financial institutions
  - POS systems

#### `owasp`
```bash
cryptex --template owasp
```
- **Standard**: OWASP Password Guidelines
- **Use cases**:
  - Web applications
  - API authentication
  - SaaS platforms
  - Security-conscious development

#### `high-security`
```bash
cryptex --template high-security
```
- **Specs**: 20+ characters, 3+ of each type
- **Use cases**:
  - Root/admin accounts
  - Database superuser passwords
  - Encryption master keys
  - SSH keys passphrases
  - Production server access
  - Secrets that protect other secrets

#### `user-friendly`
```bash
cryptex --template user-friendly
```
- **Specs**: 12 chars, no special characters, no similar chars
- **Use cases**:
  - End-user temporary passwords
  - First-time login passwords
  - Shared device access
  - Non-technical users
  - Phone dictation scenarios

#### `database`
```bash
cryptex --template database
```
- **Specs**: 16 chars, excludes quotes and backslashes
- **Use cases**:
  - MySQL/PostgreSQL passwords
  - Database connection strings
  - ORM configuration
  - Avoiding SQL escaping issues
  - Environment variables for databases

#### `wifi`
```bash
cryptex --template wifi
```
- **Specs**: 16 chars, no special characters, no similar chars
- **Use cases**:
  - Home/office WiFi passwords
  - Guest network access
  - IoT device configuration
  - Passwords typed on mobile keyboards
  - Passwords shared verbally

---

## API Key Generation

### Command
```bash
cryptex -t api-key --api-format <format>
```

### Available formats and use cases

#### `uuid`
```bash
cryptex -t api-key --api-format uuid
```
- **Output**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **Use cases**:
  - Standard API identifiers
  - Database primary keys
  - Unique resource identifiers
  - When systems expect UUID format

#### `uuid-hex`
```bash
cryptex -t api-key --api-format uuid-hex
```
- **Output**: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (no dashes)
- **Use cases**:
  - Compact identifiers
  - File names
  - URL slugs
  - When dashes cause issues

#### `base64`
```bash
cryptex -t api-key --api-format base64 -l 32
```
- **Output**: URL-safe base64 encoded
- **Use cases**:
  - JWT secrets
  - Encryption keys
  - Session tokens
  - OAuth client secrets

#### `hex`
```bash
cryptex -t api-key --api-format hex -l 32
```
- **Output**: Hexadecimal characters only
- **Use cases**:
  - Cryptographic keys
  - Hash-like identifiers
  - Low-level system tokens
  - When only hex is accepted

#### `url-safe`
```bash
cryptex -t api-key --api-format url-safe -l 32
```
- **Output**: URL-safe characters
- **Use cases**:
  - Tokens in URLs
  - Query parameters
  - Webhook secrets
  - Callback URLs with embedded tokens

#### `alphanum`
```bash
cryptex -t api-key --api-format alphanum -l 32
```
- **Output**: Letters and numbers only
- **Use cases**:
  - General API keys
  - License keys
  - Activation codes
  - Simple tokens

---

## TOTP / 2FA Generation

### What is TOTP?

TOTP (Time-based One-Time Password) is the technology behind Google Authenticator, Authy, and similar apps. It's the **6-digit code that changes every 30 seconds**.

### How TOTP Works (Step by Step)

```
┌─────────────────┐                    ┌─────────────────┐
│   YOUR SERVER   │                    │  USER'S PHONE   │
│                 │                    │  (Authenticator)│
└────────┬────────┘                    └────────┬────────┘
         │                                      │
         │  1. Generate SECRET with Cryptex     │
         │  ◄──────────────────────────────     │
         │                                      │
         │  2. Store SECRET in your database    │
         │     (linked to user account)         │
         │                                      │
         │  3. Show QR code to user             │
         │  ────────────────────────────────►   │
         │                                      │
         │  4. User scans QR code               │
         │     (now phone has same SECRET)      │
         │                                      │
         │         BOTH HAVE THE SAME SECRET    │
         │                                      │
         │  ═══════════════════════════════════ │
         │         LATER, AT LOGIN TIME:        │
         │  ═══════════════════════════════════ │
         │                                      │
         │  5. Phone shows: 847293              │
         │     (generated from SECRET + TIME)   │
         │                                      │
         │  6. User types 847293 on your site   │
         │  ◄──────────────────────────────     │
         │                                      │
         │  7. Server generates code from       │
         │     SECRET + TIME = 847293           │
         │                                      │
         │  8. Codes match? ✓ ACCESS GRANTED    │
         │                                      │
```

### The Key Concept

**The SECRET is shared between your server and the user's authenticator app.**

- Cryptex generates this SECRET
- You store it in your database
- User scans the QR to get the same SECRET in their app
- Both can now generate the same 6-digit codes independently

### Command
```bash
cryptex --totp --totp-issuer "<your-app-name>" --totp-account "<user-identifier>"
```

| Option | What it is | Example |
|--------|-----------|---------|
| `--totp-issuer` | Your application name (shown in authenticator app) | "GitHub", "MyCompany", "AdminPanel" |
| `--totp-account` | User identifier (shown in authenticator app) | "john@example.com", "admin", "user123" |

### Complete Example: Adding 2FA to Your Application

#### Step 1: Generate the TOTP secret for a user
```bash
cryptex --totp --totp-issuer "MyApp" --totp-account "john@example.com" totp_secret.json
```

Output:
```
Cryptex - TOTP Secret Generator

Issuer:  MyApp
Account: john@example.com

[QR CODE DISPLAYED HERE]

Scan the QR code above with Google Authenticator, Authy, or any TOTP app

Manual entry (if QR scan fails):
  Secret: JBSWY3DPEHPK3PXP
  Type: Time-based (TOTP)
  Algorithm: SHA1
  Digits: 6
  Period: 30 seconds
```

The file `totp_secret.json` contains:
```json
{
  "issuer": "MyApp",
  "account": "john@example.com",
  "secret": "JBSWY3DPEHPK3PXP",
  "uri": "otpauth://totp/MyApp:john@example.com?secret=JBSWY3DPEHPK3PXP&issuer=MyApp"
}
```

#### Step 2: Store the secret in your database
```sql
UPDATE users
SET totp_secret = 'JBSWY3DPEHPK3PXP'
WHERE email = 'john@example.com';
```

#### Step 3: Show QR code to user (in your web app)
Display the QR code to the user so they can scan it with their authenticator app.

#### Step 4: User scans QR code
User opens Google Authenticator → Tap "+" → Scan QR code
Now their app shows:
```
MyApp
john@example.com
847 293  (changes every 30 seconds)
```

#### Step 5: Validate the code in your application

**Python example using `pyotp` library:**
```python
import pyotp

# Get the secret from your database
user_secret = "JBSWY3DPEHPK3PXP"  # Retrieved from database

# Create TOTP object
totp = pyotp.TOTP(user_secret)

# Get the code user entered
user_code = "847293"  # From login form

# Verify it
if totp.verify(user_code):
    print("✓ 2FA verification successful!")
else:
    print("✗ Invalid code")
```

**JavaScript example using `otplib`:**
```javascript
const { authenticator } = require('otplib');

// Get the secret from your database
const userSecret = "JBSWY3DPEHPK3PXP";

// Get the code user entered
const userCode = "847293";

// Verify it
if (authenticator.verify({ token: userCode, secret: userSecret })) {
    console.log("✓ 2FA verification successful!");
} else {
    console.log("✗ Invalid code");
}
```

### Real-World Use Cases

#### Use Case 1: Admin Panel Security
```bash
# Generate 2FA for admin user
cryptex --totp --totp-issuer "Company Admin" --totp-account "admin@company.com"
```
- Store secret in admin's database record
- Require 2FA code on every admin login
- Protects against password theft

#### Use Case 2: User Self-Service 2FA Setup
```bash
# When user enables 2FA in settings
cryptex --totp --totp-issuer "MyApp" --totp-account "$USER_EMAIL" -q
```
- Generate secret when user clicks "Enable 2FA"
- Display QR code on their settings page
- Store secret after they verify it works

#### Use Case 3: Development/Testing
```bash
# Create test 2FA accounts
cryptex --totp --totp-issuer "TestApp" --totp-account "test@test.com" test_totp.json
```
- Generate test secrets for QA
- Keep test_totp.json for automated testing
- Use secret to generate valid codes in tests

#### Use Case 4: Bulk User Setup
```bash
# Generate 2FA for multiple users
for user in "alice@company.com" "bob@company.com" "carol@company.com"; do
    cryptex --totp --totp-issuer "CompanyApp" --totp-account "$user" "${user}_totp.json"
done
```

### What Goes Where

| Item | Where it goes | Why |
|------|---------------|-----|
| SECRET | Your database (encrypted) | Server needs it to verify codes |
| SECRET | User's authenticator app (via QR scan) | App needs it to generate codes |
| QR Code | Shown to user once during setup | Easy way to transfer secret to phone |
| 6-digit code | User types it at login | Proves they have the authenticator |

### Security Notes

1. **Store secrets securely** - Encrypt them in your database
2. **Show QR code only once** - During initial setup
3. **Provide backup codes** - In case user loses phone
4. **Allow recovery** - Admin reset process for locked-out users
5. **Never log secrets** - They should stay confidential

---

## TOTP Code Reader

### What is this?

The TOTP Code Reader turns Cryptex into a **CLI authenticator**. Give it a base32 secret or a QR code image, and it computes the current 6-digit TOTP code — just like Google Authenticator, but in your terminal.

### Command
```bash
cryptex --totp-code "<secret-or-image-path>"
```

### How it works

Cryptex auto-detects the input:
- If the argument is an **existing file path** → treats it as a QR code image and decodes it
- Otherwise → treats it as a **base32 TOTP secret string**

### Use cases

| Scenario | Command |
|----------|---------|
| Quick 2FA code from secret | `cryptex --totp-code "JBSWY3DPEHPK3PXP"` |
| Decode QR code image | `cryptex --totp-code ./qr-code.png` |
| Script automation | `cryptex --totp-code "$SECRET" -q` |
| Copy code to clipboard | `cryptex --totp-code "SECRET" --copy` |
| Save secret to keychain | `cryptex --totp-code ./qr.png --save-keychain --keychain-service "MyApp"` |

### Examples

#### From a base32 secret
```bash
cryptex --totp-code "JBSWY3DPEHPK3PXP"
```
Output:
```
Cryptex - TOTP Code Reader

TOTP Code: 847293
Valid for: 17 seconds
Next code: 193847
```

#### From a QR code image
```bash
cryptex --totp-code ./authenticator-qr.png
```
Output:
```
Cryptex - TOTP Code Reader

Issuer:  GitHub
Account: user@email.com

TOTP Code: 529174
Valid for: 23 seconds
Next code: 841036
```

#### Quiet mode (for scripts)
```bash
# Just the 6-digit code, nothing else
CODE=$(cryptex --totp-code "JBSWY3DPEHPK3PXP" -q)
echo "Your code is: $CODE"
```

#### Copy to clipboard
```bash
cryptex --totp-code "JBSWY3DPEHPK3PXP" --copy
```

#### Save decoded secret to keychain
```bash
# Decode QR and store the secret for future use
cryptex --totp-code ./qr.png --save-keychain --keychain-service "GitHub"
```

### Output details

- **TOTP Code**: The current 6-digit code
- **Valid for**: Seconds remaining before the code changes (color-coded: green >= 10s, yellow 5-9s, red < 5s)
- **Next code**: The code that will be active after the current one expires
- **Issuer/Account**: Shown when decoded from a QR code containing an otpauth URI

---

## QR Code Generation

### Command
```bash
cryptex --qr
```

### What it does
Displays the generated password as a QR code in the terminal.

### Use cases
- **WiFi password sharing**: Generate and display for guests to scan
- **Password handoff**: Share passwords without typing
- **Mobile device setup**: Quickly transfer passwords to phones
- **Printing**: Include QR codes in documentation

### Examples
```bash
# WiFi password with QR for guests
cryptex --template wifi --qr

# Any password with QR
cryptex -l 20 --qr

# Pronounceable password with QR
cryptex -t pronounce --qr
```

### Important note
This QR code contains the **raw password text**. It is NOT for 2FA apps.
For Google Authenticator / Authy, use `--totp` instead.

---

## Key-Value Pairs

### Command
```bash
cryptex --kv "NAME1,NAME2,NAME3"
```

### What it does
Generates multiple passwords with named keys in one command.

### Use cases
- Creating `.env` files for applications
- Bulk secret generation for microservices
- Setting up new projects with multiple secrets
- CI/CD pipeline secret initialization
- Docker/Kubernetes secret preparation

### Examples

#### Generate .env file
```bash
cryptex --kv "DATABASE_PASSWORD,REDIS_PASSWORD,JWT_SECRET,API_KEY" -f env > .env
```
Output:
```
DATABASE_PASSWORD="xK9#mL2$vN7@pQ5!"
REDIS_PASSWORD="Ht4&nB8@yM3#kL6%"
JWT_SECRET="Pw2$vC7@xN5#mK9&"
API_KEY="Qr3#tF6$wL8@yN4%"
```

#### Generate JSON for application config
```bash
cryptex --kv "db_password,cache_key,session_secret" -f json > secrets.json
```

#### Generate CSV for documentation
```bash
cryptex --kv "user1,user2,user3,user4,user5" -f csv > user_passwords.csv
```

#### Multiple secrets with high security
```bash
cryptex --kv "MASTER_KEY,ENCRYPTION_KEY,SIGNING_KEY" --template high-security -f env
```

---

## Output Formats

### Command
```bash
cryptex -f <format>
cryptex --format <format>
```

### Available formats

#### `plain` (default)
```bash
cryptex -c 3 -f plain
```
- **Output**: One password per line
- **Use cases**:
  - Terminal display
  - Piping to other commands
  - Simple scripts

#### `json`
```bash
cryptex -c 3 -f json
```
- **Output**: JSON array with id and password
- **Use cases**:
  - API responses
  - Application configuration files
  - Programmatic consumption
  - Integration with other tools

#### `csv`
```bash
cryptex -c 3 -f csv
```
- **Output**: CSV with header row
- **Use cases**:
  - Spreadsheet import
  - Bulk user creation
  - Documentation
  - Audit records

#### `env`
```bash
cryptex -c 3 -f env
```
- **Output**: Environment variable format
- **Use cases**:
  - `.env` files
  - Shell scripts
  - Docker environment files
  - CI/CD configuration

### Saving to file
```bash
cryptex -c 5 -f json passwords.json
cryptex --kv "API_KEY,DB_PASS" -f env .env
```

---

## Clipboard Integration

### Command
```bash
cryptex --copy
```

### What it does
Copies the generated password directly to system clipboard.

### Requirements
- macOS: `pbcopy` (built-in)
- Linux: `xclip` (install with `apt install xclip`)

### Use cases
- Immediate paste into password fields
- Quick password generation workflow
- Avoiding manual selection and copy

### Examples
```bash
# Generate and copy to clipboard
cryptex -l 20 --copy

# Generate high-security and copy
cryptex --template high-security --copy

# Silent generation, just copy
cryptex -q --copy
```

### Note
When generating multiple passwords, only the first is copied.

---

## Password Analysis

### Command
```bash
cryptex -v
cryptex --verbose
```

### What it does
Shows detailed analysis of generated passwords including:
- Strength score and rating
- Entropy in bits
- Character type breakdown

### Use cases
- Verifying password meets security requirements
- Educational purposes
- Security audits
- Comparing different generation options

### Example
```bash
cryptex -l 20 -v
```
Output:
```
xK9#mL2$vN7@pQ5!wR8%

Password Analysis:
Password: xK9#mL2$vN7@pQ5!wR8%
Strength: Very Strong (Score: 80/80)
Entropy: 131.09 bits
Length: 20 characters
Character types: lowercase, uppercase, digits, special
```

---

## Storage Integrations

### AWS Secrets Manager

#### Command
```bash
cryptex --save-aws --aws-secret-name "<name>" [--aws-region <region>] [--aws-profile <profile>]
```

#### Use cases
- Storing production secrets
- Team secret sharing via AWS
- Automated secret rotation
- CI/CD secret management
- Serverless application secrets

#### Examples
```bash
# Save single secret
cryptex -l 32 --save-aws --aws-secret-name "prod/database/password"

# Save with specific profile
cryptex -l 32 --save-aws --aws-secret-name "prod/api-key" --aws-profile production

# Save multiple secrets as JSON
cryptex --kv "DB_PASS,API_KEY" --save-aws --aws-secret-name "myapp/secrets"

# Different region
cryptex --save-aws --aws-secret-name "eu-secrets" --aws-region eu-west-1
```

---

### HashiCorp Vault

#### Command
```bash
cryptex --save-vault --vault-path "<path>" [--vault-url <url>]
```

#### Requirements
Set environment variable: `export VAULT_TOKEN=your-token`

#### Use cases
- Enterprise secret management
- Dynamic secret generation
- Secret versioning and audit
- Multi-environment deployments
- Kubernetes secret injection

#### Examples
```bash
# Save to default Vault
cryptex -l 24 --save-vault --vault-path "secret/myapp/database"

# Save multiple secrets
cryptex --kv "api_key,webhook_secret" --save-vault --vault-path "secret/myapp/keys"

# Custom Vault server
cryptex --save-vault --vault-path "secret/prod" --vault-url "https://vault.company.com"
```

---

### OS Keychain

#### Command
```bash
cryptex --save-keychain --keychain-service "<service>" --keychain-account "<account>"
```

#### Platforms
- macOS: Keychain Access
- Linux: GNOME Keyring / KWallet
- Windows: Credential Manager

#### Use cases
- Personal password storage
- Development machine secrets
- Local application credentials
- Secure local backup of passwords

#### Examples
```bash
# Save single password
cryptex -l 20 --save-keychain --keychain-service "MyApp" --keychain-account "admin"

# Save multiple passwords
cryptex --kv "dev,staging,prod" --save-keychain --keychain-service "DatabasePasswords"

# Retrieve later (macOS)
security find-generic-password -s "MyApp" -a "admin" -w
```

---

## Quiet Mode

### Command
```bash
cryptex -q
cryptex --quiet
```

### What it does
Suppresses all output except the password itself (no banner, no messages).

### Use cases
- Shell scripts and automation
- Piping to other commands
- CI/CD pipelines
- Programmatic password generation
- When only the password matters

### Examples
```bash
# Just the password, nothing else
cryptex -q -l 20

# Use in scripts
PASSWORD=$(cryptex -q -l 32)

# Pipe to another command
cryptex -q | xargs echo "Your password is:"

# Silent save to AWS
cryptex -q --save-aws --aws-secret-name "prod/secret"
```

---

## Multiple Passwords

### Command
```bash
cryptex -c <count>
cryptex --count <count>
```

### Use cases
- Bulk user password generation
- Creating password pools
- Multiple environment secrets
- Backup password generation

### Examples
```bash
# Generate 10 passwords
cryptex -c 10

# Generate 5 high-security passwords as JSON
cryptex -c 5 --template high-security -f json

# Generate 100 user passwords to CSV
cryptex -c 100 --template user-friendly -f csv > new_users.csv
```

---

## Custom Separator

### Command
```bash
cryptex --separator "<sep>"
```

### Use cases
- Custom output formatting
- Integration with specific tools
- One-line password lists

### Examples
```bash
# Comma-separated passwords
cryptex -c 5 --separator ","

# Space-separated
cryptex -c 3 --separator " "

# Custom delimiter
cryptex -c 3 --separator " | "
```

---

## Common Workflows

### New Project Setup
```bash
# Generate all secrets for a new project
cryptex --kv "DATABASE_URL,REDIS_URL,SESSION_SECRET,API_KEY,JWT_SECRET" \
  --template high-security -f env > .env
```

### New User Onboarding
```bash
# Generate temporary password for new user
cryptex --template user-friendly --copy
```

### WiFi Password Change
```bash
# Generate new WiFi password with QR
cryptex --template wifi --qr
```

### Production Deployment
```bash
# Generate and store production secrets
cryptex -q --template high-security \
  --save-aws --aws-secret-name "prod/app/master-key" \
  --aws-profile production
```

### 2FA Setup for Application
```bash
# Generate TOTP for admin account
cryptex --totp --totp-issuer "MyCompany Admin" --totp-account "admin@company.com"
```

### Database Password Rotation
```bash
# Generate database-safe password and save
cryptex --template database \
  --save-vault --vault-path "secret/db/password-$(date +%Y%m%d)"
```

---

## Quick Reference

| Need | Command |
|------|---------|
| Basic password | `cryptex` |
| Longer password | `cryptex -l 24` |
| No special chars | `cryptex --template user-friendly` |
| For WiFi | `cryptex --template wifi --qr` |
| For database | `cryptex --template database` |
| For admin | `cryptex --template high-security` |
| API key | `cryptex -t api-key --api-format uuid` |
| 2FA setup | `cryptex --totp --totp-issuer "App" --totp-account "user"` |
| Read TOTP code | `cryptex --totp-code "SECRET"` |
| Read TOTP from QR | `cryptex --totp-code ./qr.png` |
| Multiple secrets | `cryptex --kv "A,B,C" -f env` |
| Copy to clipboard | `cryptex --copy` |
| Save to AWS | `cryptex --save-aws --aws-secret-name "name"` |
| Silent mode | `cryptex -q` |
