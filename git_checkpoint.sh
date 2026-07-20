#!/bin/bash
# git_checkpoint.sh

if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
fi

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
MESSAGE=${1:-"Automatic checkpoint: $TIMESTAMP"}

git add .
git commit -m "$MESSAGE"

echo "Checkpoint saved: $MESSAGE"
