#!/usr/bin/env python3
"""
Generate previews.json file for Cabinet Designer preview index.

NOTE: This script is no longer used by the automated workflow.
The preview-index.html now fetches branch/PR data on-demand from GitHub API.

This script can still be used manually if you want to pre-generate a
previews.json file for offline use or testing.

This script fetches branch and PR information from GitHub API and generates
a previews.json file with dynamic preview URLs.
"""

import json
import os
import requests
import argparse
from datetime import datetime

def get_github_branches(repo_owner, repo_name, github_token=None):
    """Fetch all branches from GitHub repository."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/branches"
    headers = {}
    
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching branches: {e}")
        return []

def get_github_pull_requests(repo_owner, repo_name, github_token=None):
    """Fetch all open pull requests from GitHub repository."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls?state=open"
    headers = {}
    
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching pull requests: {e}")
        return []

def generate_preview_data(branches, pull_requests):
    """Generate preview data from branches and PRs using dynamic preview URLs."""
    previews = []
    base_url = "https://nothinn.github.io/cabinet-designer"

    # Add production preview (main branch)
    main_branch = next((b for b in branches if b["name"] == "main"), None)
    if main_branch:
        # Handle different branch data structures
        if "commit" in main_branch and isinstance(main_branch["commit"], dict):
            commit_date = main_branch["commit"].get("commit", {}).get("author", {}).get("date", main_branch["commit"].get("commit", {}).get("committer", {}).get("date", ""))
        else:
            commit_date = ""

        previews.append({
            "name": "main",
            "url": f"{base_url}/",
            "type": "production",
            "updated_at": commit_date or datetime.utcnow().isoformat() + "Z"
        })

    # Add branch previews (excluding main) - use dynamic preview URLs
    for branch in branches:
        if branch["name"] == "main":
            continue

        # Handle different branch data structures
        if "commit" in branch and isinstance(branch["commit"], dict):
            commit_date = branch["commit"].get("commit", {}).get("author", {}).get("date", branch["commit"].get("commit", {}).get("committer", {}).get("date", ""))
        else:
            commit_date = ""

        previews.append({
            "name": branch["name"],
            "url": f"{base_url}/preview.html?branch={branch['name']}",
            "type": "branch",
            "updated_at": commit_date or datetime.utcnow().isoformat() + "Z"
        })

    # Add PR previews - use dynamic preview URLs
    for pr in pull_requests:
        previews.append({
            "name": f"pr-{pr['number']}-{pr['head']['ref']}",
            "url": f"{base_url}/preview.html?pr={pr['number']}",
            "type": "pr",
            "updated_at": pr["updated_at"]
        })

    return previews

def write_previews_json(previews, output_file="previews.json"):
    """Write preview data to JSON file."""
    data = {
        "previews": previews,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "count": len(previews)
    }
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Successfully generated {output_file} with {len(previews)} previews")
        return True
    except IOError as e:
        print(f"Error writing {output_file}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate previews.json for Cabinet Designer")
    parser.add_argument("--repo-owner", default="nothinn", help="GitHub repository owner")
    parser.add_argument("--repo-name", default="cabinet-designer", help="GitHub repository name")
    parser.add_argument("--output", default="previews.json", help="Output JSON file")
    parser.add_argument("--github-token", help="GitHub personal access token (optional)")
    
    args = parser.parse_args()
    
    print(f"🔍 Fetching data from {args.repo_owner}/{args.repo_name}...")
    
    # Fetch branches
    branches = get_github_branches(args.repo_owner, args.repo_name, args.github_token)
    print(f"📋 Found {len(branches)} branches")
    
    # Fetch pull requests
    pull_requests = get_github_pull_requests(args.repo_owner, args.repo_name, args.github_token)
    print(f"📝 Found {len(pull_requests)} open pull requests")
    
    # Generate preview data
    previews = generate_preview_data(branches, pull_requests)
    print(f"🎯 Generated {len(previews)} preview entries")
    
    # Write to file
    success = write_previews_json(previews, args.output)
    
    if success:
        print(f"📄 Preview data written to {args.output}")
        print(f"📊 Summary: {len(previews)} previews (1 production, {len(branches)-1} branches, {len(pull_requests)} PRs)")
    else:
        print("❌ Failed to write preview data")
        return 1
    
    return 0

if __name__ == "__main__":
    main()