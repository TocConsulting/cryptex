# Cryptex Roadmap

Future features and enhancements planned for Cryptex.

---

## Planned Features

### Passphrase Generation

Generate memorable passphrases using dictionary words (similar to Diceware).

- Dictionary-based word selection
- Configurable word count and separators
- Multiple language support
- Custom word lists

```bash
cryptex --type passphrase --words 6 --separator -
```

---

### Container and Kubernetes Integration

Native support for container secret management.

- Docker secrets integration
- Kubernetes Secret object generation
- Helm values file generation

```bash
cryptex -c 5 --k8s-secret myapp-secrets
```

---

### Password Manager Export

Direct export to popular password managers.

Supported formats:
- 1Password
- Bitwarden
- KeePass
- LastPass

```bash
cryptex -l 20 --export bitwarden
```

---

### Password Rotation Scheduler

Automated password rotation with scheduling.

- Cron-style scheduling
- CI/CD integration
- Webhook notifications

```bash
cryptex rotate --schedule "0 0 1 * *" --notify webhook
```

---

### Encrypted Bundle Export

Secure password bundle sharing.

- Encrypted password sets
- Time-based expiration
- One-time download links

```bash
cryptex bundle create --expire 24h --encrypt
```

---

### Password Strength API

REST API for password validation and generation.

- Strength checking endpoint
- Policy validation
- Bulk operations

```bash
cryptex serve --port 8080
```

---

## Contributing

Contributions are welcome. If you want to work on any of these features, please open an issue first to discuss the implementation approach.
