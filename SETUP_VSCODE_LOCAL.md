# Second Brain — Local VS Code Setup Guide
> For contributors who want to work locally on their own machine instead of Codespaces.

---

## Step 1 — Install Python 3.11

1. Go to [python.org/downloads](https://python.org/downloads)
2. Download **Python 3.11** (not 3.12 or 3.13 — some ML packages lag behind)
3. Run the installer
   - **Windows:** Check the box that says **"Add Python to PATH"** before clicking Install
   - **Mac:** Just run the `.pkg` file
4. Verify it worked — open a terminal and run:

```bash
python --version
```
Expected: `Python 3.11.x`

---

## Step 2 — Install Git

1. Go to [git-scm.com/downloads](https://git-scm.com/downloads)
2. Download and run the installer (leave all default options as-is)
3. After install, open a terminal and configure your identity:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@email.com"
```

Use the same email as your GitHub account.

---

## Step 3 — Install Docker Desktop

Docker runs the Qdrant vector database on your machine without you having to install it manually.

1. Go to [docker.com/products/docker-desktop](https://docker.com/products/docker-desktop)
2. Download the version for your OS and run the installer
3. Open Docker Desktop and let it finish starting up (the whale icon in your menu bar should stop animating)
4. Verify in terminal:

```bash
docker --version
```
Expected: `Docker version 24.x.x` or higher

---

## Step 4 — Install VS Code

1. Go to [code.visualstudio.com](https://code.visualstudio.com)
2. Download and install it
3. Open VS Code, then install these extensions (click the Extensions icon on the left sidebar):
   - **Python** (by Microsoft)
   - **Pylance** (by Microsoft)
   - **GitLens** (optional but useful for seeing what your partner changed)

---

## Step 5 — Clone the repository

This downloads the project to your computer.

```bash
cd ~/Desktop
git clone https://github.com/ParthAwade10/Second-Brain.git
cd Second-Brain
```

Then open the folder in VS Code:

```bash
code .
```

---

## Step 6 — Create your own branch

Never work on `main` directly. Create your own branch:

```bash
git checkout -b your_name_branch
```

---

## Step 7 — Install dependencies

```bash
pip install -r requirements.txt
```

This will take 2–3 minutes. Wait for it to fully complete.

> No virtual environment needed — pip will install packages globally on your machine. If you ever work on multiple Python projects simultaneously, revisit this and set up venv at that point.

---

## Step 8 — Set up your API keys

Everyone on the team needs their own Anthropic API key. Go to [console.anthropic.com](https://console.anthropic.com), create an account, and generate a key.

Then create a `.env` file in the root of the project:

```bash
touch .env        # Mac/Linux
type nul > .env   # Windows
```

Open it and add:

```
ANTHROPIC_API_KEY=sk-ant-...
```

> **The `.env` file is already in `.gitignore` — it will never be uploaded to GitHub.** Each person has their own key in their own `.env` file. Never put your key anywhere else in the code.

Verify it loaded correctly:

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY')[:12])"
```

Expected output: `sk-ant-api03`

---

## Step 9 — Start the vector database

Make sure Docker Desktop is open first, then run:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

Leave this running in its own terminal. Open a second terminal for all other work.

Verify it's running: open [http://localhost:6333/dashboard](http://localhost:6333/dashboard) in your browser — you should see the Qdrant UI.

---

## Step 10 — Confirm the folder structure looks right

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

Every time you sit down to work:

```bash
# 1. Navigate to the project
cd ~/Desktop/Second-Brain

# 2. Pull latest changes from main
git pull origin main

# 3. Open Docker Desktop, then start Qdrant in a separate terminal
docker run -p 6333:6333 qdrant/qdrant
```

---

## Saving and sharing your work

```bash
# Stage all your changes
git add .

# Commit with a clear message describing what you did
git commit -m "add cross-encoder reranker"

# Push your branch to GitHub
git push origin your_name_branch
```

Then go to [github.com/ParthAwade10/Second-Brain](https://github.com/ParthAwade10/Second-Brain) and open a **Pull Request** from your branch into `main`. Tag Parth to review before merging.

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

## Troubleshooting

**`python` not found on Windows**
Run `py` instead of `python`, or re-install Python and make sure "Add to PATH" is checked.

**`pip install` fails with permissions error**
Add `--user` flag: `pip install --user -r requirements.txt`

**Docker says "cannot connect to Docker daemon"**
Make sure Docker Desktop is open and fully started (the whale icon is static, not spinning).

**Port 6333 already in use**
Another Qdrant instance is already running. Run:
```bash
docker ps
docker stop <container_id>
```
Then start it again.
