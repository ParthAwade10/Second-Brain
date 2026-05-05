# Second Brain — Codespace Setup Guide
> For contributors joining the project via GitHub Codespaces. No local installs needed.

---

## Prerequisites

- A GitHub account
- Access to the `Second-Brain` repository (ask Parth to add you as a collaborator)

---

## Step 1 — Accept the collaborator invite

Parth will send you a GitHub collaborator invite to your email. Accept it. You should now see the `Second-Brain` repo under your GitHub account.

---

## Step 2 — Open the repo in a Codespace

1. Go to the repo on GitHub: `github.com/ParthAwade10/Second-Brain`
2. Click the green **Code** button
3. Click the **Codespaces** tab
4. Click **Create codespace on main**

GitHub will spin up a cloud machine for you with VS Code in your browser. This takes about 60 seconds.

---

## Step 3 — Create your own branch

Every contributor works on their own branch — never commit directly to `main`.

In the terminal at the bottom of the Codespace (Terminal → New Terminal):

```bash
git checkout -b your_name_branch
```

For example:
```bash
git checkout -b alex_branch
```

You should see:
```
Switched to a new branch 'alex_branch'
```

---

## Step 4 — Verify your environment

Run these one at a time and confirm each prints a version number:

```bash
python --version
```
Expected: `Python 3.12.x`

```bash
docker --version
```
Expected: `Docker version 29.x.x`

```bash
pip --version
```
Expected: `pip 26.x.x`

---

## Step 5 — Install dependencies

```bash
pip install -r requirements.txt
```

This will take 2–3 minutes. Wait for it to fully complete before moving on.

---

## Step 6 — Set up your API keys

Everyone on the team needs their own Anthropic API key. Go to [console.anthropic.com](https://console.anthropic.com), create an account, and generate a key.

Then create a `.env` file in the root of the project:

```bash
touch .env
```

Open it in the editor and add:

```
ANTHROPIC_API_KEY=sk-ant-...
```

> **Important:** The `.env` file is already in `.gitignore` — it will never be uploaded to GitHub. Never paste your API key anywhere else in the codebase. Each person has their own key in their own `.env` file.

Verify it loaded correctly:

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY')[:12])"
```

Expected output: `sk-ant-api03`

---

## Step 7 — Start the vector database

Qdrant is the database that stores your document embeddings. Start it with Docker:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

Leave this running in its own terminal tab. Open a second terminal (click the `+` in the terminal panel) for all your other work.

You can verify it's running by visiting: `http://localhost:6333/dashboard` in your browser.

---

## Step 8 — Confirm the folder structure looks right

```bash
ls
```

You should see:

```
ingestion/
retrieval/
agents/
evals/
tests/
data/
main.py
config.py
requirements.txt
.env
.gitignore
README.md
```

---

## Daily workflow

Every time you come back to work:

```bash
# 1. Pull latest changes from main
git pull origin main

# 2. Start Qdrant in a separate terminal tab
docker run -p 6333:6333 qdrant/qdrant
```

That's it — no environment to activate, just pull and run.

---

## Saving and sharing your work

When you've made changes you want to save and share:

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "add BM25 sparse retrieval"

# Push to GitHub
git push origin your_name_branch
```

Then go to GitHub and open a **Pull Request** from your branch into `main`. Tag Parth to review it before merging.

---

## Folder ownership

| Folder | Owner |
|--------|-------|
| `ingestion/` | Parth |
| `evals/` | Parth |
| `retrieval/` | You |
| `agents/` | You |

Don't edit files outside your folders without checking with the other person first.

---

## Getting help

- Ask in your group chat
- Open a GitHub Issue on the repo describing what's broken
- Tag the relevant person in the issue
