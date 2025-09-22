# Deployment Guide

## 🚀 Quick Deploy to GitHub Actions

### Step 1: Fork Repository
1. Click "Fork" on this repository
2. Clone your fork locally

### Step 2: Set up Supabase
1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Run the SQL from `supabase_schema_updated.sql` in the SQL Editor
4. Note your project URL and anon key

### Step 3: Get OpenAI API Key
1. Go to [platform.openai.com](https://platform.openai.com)
2. Create an API key
3. Note the key

### Step 4: Configure GitHub Secrets
1. Go to your GitHub repo → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon key

### Step 5: Enable GitHub Actions
1. Go to Actions tab in your repo
2. Enable workflows if prompted
3. The workflow will run automatically every 30 minutes

## 🔧 Manual Testing

```bash
# Test locally
uv run python main.py

# Check GitHub Actions
# Go to Actions tab → Check workflow runs
```

## 📊 Monitoring

- **GitHub Actions**: Check run logs and status
- **Supabase**: View articles in your database
- **Console**: See processing logs in real-time

## 🛠️ Troubleshooting

### Common Issues:

1. **"Could not find the table"**
   - Solution: Run the SQL schema in Supabase

2. **"Invalid API key"**
   - Solution: Check your environment variables

3. **"No new articles found"**
   - Solution: Check if feeds are working, reset state if needed

4. **Workflow not running**
   - Solution: Check if GitHub Actions is enabled

