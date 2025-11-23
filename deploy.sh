#!/bin/bash
echo "🚀 Deploying Smart Finance Tracker..."

# Step 1: Git
git add .
git commit -m "deploy: $(date)"
git push origin main

# Step 2: Railway deploy
git push railway main

echo "✅ Deployment completed! Check your Railway dashboard"