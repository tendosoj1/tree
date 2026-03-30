# review.py
import os, sys, json
import urllib.request

def get_pr_diff():
    repo    = os.environ["GITHUB_REPOSITORY"]
    pr_num  = os.environ["PR_NUMBER"]
    token   = os.environ["GITHUB_TOKEN"]
    url     = f"https://api.github.com/repos/{repo}/pulls/{pr_num}/files"
    req     = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    })
    with urllib.request.urlopen(req) as r:
        files = json.loads(r.read())
    return "\n\n".join(
        f"### {f['filename']}\n{f.get('patch','(binary or no diff)')}"
        for f in files
    )

def ask_claude(diff):
    key  = os.environ["ANTHROPIC_API_KEY"]
    body = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1024,
        "messages": [{
            "role": "user",
            "content": (
                "You are a senior code reviewer. Review the following "
                "PR diff and give clear, constructive feedback.\n\n"
                "Focus on: bugs, security issues, ML best practices, "
                "performance, and readability.\n\n"
                f"{diff}"
            )
        }]
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    )
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read())
    return data["content"][0]["text"]

def post_comment(review):
    repo   = os.environ["GITHUB_REPOSITORY"]
    pr_num = os.environ["PR_NUMBER"]
    token  = os.environ["GITHUB_TOKEN"]
    url    = f"https://api.github.com/repos/{repo}/issues/{pr_num}/comments"
    body   = json.dumps({"body": f"## 🤖 Claude Code Review\n\n{review}"}).encode()
    req    = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json"
    })
    urllib.request.urlopen(req)
    print("Review posted!")

if __name__ == "__main__":
    diff   = get_pr_diff()
    review = ask_claude(diff)
    post_comment(review)
