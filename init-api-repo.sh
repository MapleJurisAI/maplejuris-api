#!/usr/bin/env bash
# MapleJuris API Bootstrap / Initializer using Pipenv
# Fully automated: Python install, Pipenv, folders, files, dev tools, .env handling

set -euo pipefail
IFS=$'\n\t'

REPO_NAME="maplejuris-api"
REPO_PATH="repos/$REPO_NAME"
LOCAL_KEY_DIR="$HOME/.maplejuris"
PRIVATE_KEY_FILE="$LOCAL_KEY_DIR/age-key.txt"

# -----------------------------
# 1️⃣ Check repo exists
# -----------------------------
if [ ! -d "$REPO_PATH" ]; then
    echo "❌ Repository '$REPO_NAME' not found in repos/"
    echo "➡ Please run: bash clone-all-repos.sh"
    exit 1
fi

# -----------------------------
# 2️⃣ Copy initializer to repo root
# -----------------------------
if [ "$(basename "$0")" != "init-api-repo.sh" ] || [ ! -f "$REPO_PATH/init-api-repo.sh" ]; then
    echo "📁 Copying initializer to repo root..."
    cp "$0" "$REPO_PATH/init-api-repo.sh"
    chmod +x "$REPO_PATH/init-api-repo.sh"
fi

cd "$REPO_PATH"

# -----------------------------
# 3️⃣ Ensure Python
# -----------------------------
echo "🔍 Checking Python..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "⚠️ Python not found. Installing latest Python via pyenv..."
    if ! command -v pyenv >/dev/null 2>&1; then
        curl https://pyenv.run | bash
        export PATH="$HOME/.pyenv/bin:$PATH"
        eval "$(pyenv init -)"
        eval "$(pyenv virtualenv-init -)"
    fi
    LATEST_PY=$(pyenv install -l | grep -E "3\.[0-9]+\.[0-9]+" | tail -1 | tr -d ' ')
    pyenv install -s "$LATEST_PY"
    pyenv global "$LATEST_PY"
fi

PYTHON_BIN=$(command -v python3 || command -v python)
echo "✅ Using Python: $PYTHON_BIN"

# -----------------------------
# 4️⃣ Ensure Pipenv
# -----------------------------
if ! command -v pipenv >/dev/null 2>&1; then
    echo "⬇ Installing Pipenv..."
    $PYTHON_BIN -m pip install --user pipenv

    # Add user-local bin to PATH (cross-platform macOS/Linux)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        export PATH="$HOME/Library/Python/$(python3 -c 'import sys; print(".".join(map(str,sys.version_info[:2])))')/bin:$PATH"
    else
        export PATH="$HOME/.local/bin:$PATH"
    fi
fi

# Confirm pipenv available
command -v pipenv >/dev/null 2>&1 || { echo "❌ Pipenv not found in PATH"; exit 1; }

# -----------------------------
# 5️⃣ Folder structure
# -----------------------------
folders=(
    "agents" "clients" "graphs" "schemas" "prompt_templates"
    "tests" "tests/unit_tests" "tests/integration_tests"
    "tests/end_to_end_tests" "tests/load_tests"
    "examples" "database" "artifacts"
)

for folder in "${folders[@]}"; do
    mkdir -p "$folder"
done

# -----------------------------
# 6️⃣ __init__.py files
# -----------------------------
init_files=(
    "agents/__init__.py" "graphs/__init__.py" "schemas/__init__.py"
    "prompt_templates/__init__.py" "clients/__init__.py" "tests/__init__.py"
    "tests/unit_tests/__init__.py" "tests/integration_tests/__init__.py"
    "tests/end_to_end_tests/__init__.py" "tests/load_tests/__init__.py"
    "examples/__init__.py" "database/__init__.py" "artifacts/__init__.py"
)

for file in "${init_files[@]}"; do
    touch "$file"
done

# -----------------------------
# 7️⃣ Placeholder files
# -----------------------------
files=(
    "agents/chat_agent.py" "graphs/chat_graph.py"
    "schemas/chat_agent_schemas.py" "schemas/chat_graph_schemas.py" "schemas/chat_agent_examples_schemas.py"
    "prompt_templates/chat_agent_prompt_template_system.md" "prompt_templates/chat_agent_prompt_template_human.md"
    "prompt_templates/prompt_template_loader.py"
    ".env" ".gitignore"
)

for file in "${files[@]}"; do
    [ ! -f "$file" ] && touch "$file"
done

# -----------------------------
# 8️⃣ Pipenv install dependencies
# -----------------------------
pipenv install fastapi uvicorn pydantic sqlalchemy
pipenv install --dev black isort autoflake ruff mypy pre-commit sops age

# -----------------------------
# 9️⃣ Pre-commit config
# -----------------------------
cat > ".pre-commit-config.yaml" << 'EOF'
repos:
  - repo: https://github.com/PyCQA/autoflake
    rev: v2.2.1
    hooks:
      - id: autoflake
        args: [--remove-all-unused-imports, --remove-unused-variables, --in-place]

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--filter-files", "--profile", "black"]

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
EOF

pipenv run pre-commit install

# -----------------------------
# 🔐 10️⃣ Handle .env / .env.enc
# -----------------------------
mkdir -p "$LOCAL_KEY_DIR"

if [ -f ".env.enc" ] && [ -f "$PRIVATE_KEY_FILE" ]; then
    export SOPS_AGE_KEY_FILE="$PRIVATE_KEY_FILE"
    pipenv run sops --decrypt .env.enc > .env
    echo "🔓 Decrypted .env from .env.enc"
elif [ ! -f ".env" ]; then
    touch .env
fi

# -----------------------------
# 🎉 11️⃣ Done
# -----------------------------
echo ""
echo "===================================="
echo "🎉 $REPO_NAME initialized successfully!"
echo "✅ Pipenv virtualenv ready, dependencies installed"
echo "✅ Folders, files, pre-commit, .env ready"
echo ""
echo "➡ To start:"
echo "  cd $REPO_PATH"
echo "  pipenv shell"
echo "===================================="