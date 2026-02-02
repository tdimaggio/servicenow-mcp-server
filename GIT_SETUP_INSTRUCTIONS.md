# Git Setup Instructions

## Repository Organization

Your repository is now organized for GitHub:

### Files to Push (Essential):
```
├── README.md                      # Main documentation
├── server.py                      # MCP server code
├── test_connection.py             # Connection test script
├── test_all_tools.py              # Tool verification script
├── add_table_permissions.js       # ServiceNow permission script
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
└── GIT_SETUP_INSTRUCTIONS.md      # Git workflow guide (this file)
```

### Files NOT Pushed (Local/Ignored):
```
├── .env                           # Your credentials (ignored)
├── .claude/                       # Claude config (ignored)
├── venv/                          # Python environment (ignored)
└── artifacts/                     # Development notes (ignored)
    ├── MCP_SERVER_ENHANCEMENTS.md
    ├── ServiceNow_MCP_Server_Setup_Guide 1.txt
    ├── mcp_setup_conversation.txt
    └── table_permissions_needed.md
```

---

## First-Time Git Setup

### Step 1: Initialize Git Repository

```bash
cd ~/Projects/claude_mcp
git init
```

### Step 2: Configure Git (If Not Already Done)

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Step 3: Stage All Files

```bash
git add .
```

This will add all files EXCEPT those in `.gitignore`:
- ✓ README.md
- ✓ server.py
- ✓ test_connection.py
- ✓ test_all_tools.py
- ✓ add_table_permissions.js
- ✓ requirements.txt
- ✓ .gitignore
- ✗ .env (ignored - contains secrets)
- ✗ venv/ (ignored - local environment)
- ✗ artifacts/ (ignored - development notes)
- ✗ .claude/ (ignored - local config)

### Step 4: Verify What Will Be Committed

```bash
git status
```

Expected output:
```
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
        new file:   .gitignore
        new file:   README.md
        new file:   add_table_permissions.js
        new file:   requirements.txt
        new file:   server.py
        new file:   test_all_tools.py
        new file:   test_connection.py
```

**Important:** Make sure `.env` and `venv/` are NOT listed!

### Step 5: Create Initial Commit

```bash
git commit -m "Initial commit: ServiceNow MCP Server

- Add comprehensive README with setup instructions
- Add MCP server with 9 working tools
- Add test scripts for connection and tool verification
- Add ServiceNow permission configuration script
- Add Python dependencies list"
```

---

## Push to GitHub

### Step 6: Create GitHub Repository

1. Go to [github.com](https://github.com)
2. Click the **+** icon in the top right > **New repository**
3. Fill in:
   - **Repository name**: `servicenow-mcp-server` (or your preferred name)
   - **Description**: "Connect Claude Desktop to ServiceNow for debugging and monitoring"
   - **Visibility**: Public or Private (your choice)
   - **Do NOT initialize** with README, .gitignore, or license (we already have these)
4. Click **Create repository**

### Step 7: Connect Local Repo to GitHub

Copy the commands from GitHub (should look like this):

```bash
git remote add origin https://github.com/YOUR_USERNAME/servicenow-mcp-server.git
git branch -M main
git push -u origin main
```

**Or if you prefer SSH:**

```bash
git remote add origin git@github.com:YOUR_USERNAME/servicenow-mcp-server.git
git branch -M main
git push -u origin main
```

### Step 8: Verify on GitHub

1. Refresh your GitHub repository page
2. Verify all files are present
3. Check that README.md displays correctly
4. Confirm `.env` and `venv/` are NOT uploaded

---

## Future Updates

### Making Changes

After you make changes to any files:

```bash
# Check what changed
git status

# Stage specific files
git add server.py README.md

# Or stage all changes
git add .

# Commit with descriptive message
git commit -m "Add new tool for querying incident table"

# Push to GitHub
git push
```

### Useful Git Commands

```bash
# View commit history
git log --oneline

# See what changed in files
git diff

# Undo changes to a file (before staging)
git checkout -- filename

# Undo last commit (keep changes)
git reset --soft HEAD~1

# View remote repository URL
git remote -v

# Create a new branch
git checkout -b feature-name

# Switch branches
git checkout main
```

---

## Adding a LICENSE

GitHub will prompt you to add a license. For open source:

### Option 1: Add via GitHub Web Interface
1. Go to your repository on GitHub
2. Click "Add file" > "Create new file"
3. Name it `LICENSE`
4. Click "Choose a license template"
5. Select **MIT License** (recommended for open source)
6. Fill in the year and your name
7. Commit directly to main branch

### Option 2: Add via Command Line

```bash
# Create LICENSE file locally
touch LICENSE

# Add MIT License content (example)
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# Commit and push
git add LICENSE
git commit -m "Add MIT License"
git push
```

---

## Repository Settings (Optional)

### Add Topics (Tags)
On GitHub, click the gear icon next to "About" and add topics:
- `servicenow`
- `mcp`
- `claude`
- `debugging`
- `python`
- `mcp-server`

### Enable GitHub Pages (for docs)
1. Go to Settings > Pages
2. Source: Deploy from branch
3. Branch: main, folder: / (root)
4. Your README will be viewable at: `https://YOUR_USERNAME.github.io/servicenow-mcp-server`

### Add Repository Description
Click the gear icon next to "About" and add:
- **Description**: "Connect Claude Desktop to ServiceNow for comprehensive debugging and monitoring through natural conversation"
- **Website**: (your docs URL if using GitHub Pages)

---

## Security Checklist

Before pushing, verify:

- ✅ `.env` file is in `.gitignore`
- ✅ No credentials in any committed files
- ✅ `venv/` directory is in `.gitignore`
- ✅ No ServiceNow instance URLs in committed code (use environment variables)
- ✅ Run: `git log --all -- .env` (should show nothing)

If you accidentally committed `.env`:

```bash
# Remove from git but keep local file
git rm --cached .env

# Commit the removal
git commit -m "Remove .env from version control"

# Push
git push

# For extra security, change your ServiceNow password
```

---

## Troubleshooting

### "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/servicenow-mcp-server.git
```

### "Permission denied (publickey)"
You need to set up SSH keys or use HTTPS instead:
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/servicenow-mcp-server.git
```

### ".env file was pushed to GitHub!"
1. Remove it immediately: `git rm --cached .env`
2. Commit and push: `git commit -m "Remove credentials" && git push`
3. Change your ServiceNow password immediately
4. Rotate any exposed credentials
5. Consider the repository compromised if it's public

---

## Success Checklist

After pushing, verify:

- ✅ Repository is visible on GitHub
- ✅ README displays correctly with formatting
- ✅ All 7 essential files are present
- ✅ `.env` is NOT visible in the repository
- ✅ `venv/` is NOT visible in the repository
- ✅ `artifacts/` is NOT visible in the repository
- ✅ You can clone the repo to a different location and it works

Test clone:
```bash
cd ~/Desktop
git clone https://github.com/YOUR_USERNAME/servicenow-mcp-server.git test-clone
cd test-clone
ls -la
# Should see all files except .env, venv/, artifacts/
```

---

**You're all set! Your ServiceNow MCP Server is now on GitHub! 🎉**
