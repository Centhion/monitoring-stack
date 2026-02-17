# SSH Authentication for Git

## Overview

This project uses SSH for Git authentication. SSH provides secure, passwordless authentication to GitHub/GitLab without requiring Personal Access Tokens.

## Option 1: Password Manager SSH Agent (Recommended)

Modern password managers can act as SSH agents, providing secure key storage with biometric unlock.

### 1Password

1. Enable SSH Agent in 1Password:
   - Open 1Password > Settings > Developer
   - Enable "Use the SSH Agent"

2. Configure SSH to use 1Password agent:
   ```bash
   # ~/.ssh/config
   Host *
       IdentityAgent "~/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock"
   ```

3. Add your SSH key to 1Password (or generate one within 1Password)

### Other Password Managers

- **Bitwarden**: Use Bitwarden SSH Agent extension
- **Dashlane**: Supports SSH key storage
- **Keeper**: Has SSH key management

## Option 2: Standard SSH Keys

If you prefer traditional SSH keys:

1. Generate a key (if you don't have one):
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. Add to SSH agent:
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```

3. Add public key to GitHub:
   - Copy: `cat ~/.ssh/id_ed25519.pub`
   - GitHub > Settings > SSH Keys > New SSH Key

## Verification

Test authentication:

```bash
ssh -T git@github.com
```

Expected output:
```
Hi <username>! You've successfully authenticated...
```

## Git Remote Setup

Always use SSH format for remotes:

```bash
# Correct (SSH)
git remote add origin git@github.com:username/repo.git

# Avoid (HTTPS - requires tokens)
git remote add origin https://github.com/username/repo.git
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Permission denied | Verify key is added to GitHub and SSH agent is running |
| Agent not running | Run `eval "$(ssh-agent -s)"` or open your password manager |
| Wrong key used | Check `~/.ssh/config` for correct IdentityFile/IdentityAgent |

## Platform Notes

| Platform | Default SSH Config Location |
|----------|----------------------------|
| macOS | `~/.ssh/config` |
| Linux | `~/.ssh/config` |
| Windows | `C:\Users\<user>\.ssh\config` |
