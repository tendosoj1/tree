
# review.py (fixed)
import os, sys, json
import urllib.request
import urllib.error

def get_pr_diff():
    repo    = os.environ["GITHUB_REPOSITORY"]
    pr_num  = os.environ["PR_NUMBER"]
    token   = os.environ["GITHUB_TOKEN"]
    url     = f"https://api.github.com/repos/{repo}/pulls/{pr_num}/files"
    req     = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "claude-reviewer"
    })
    with urllib.request.urlopen(req) as r:
        files = json.loads(r.read())
    patches = []
    for f in files:
        patch = f.get("patch", "(binary or no diff)")
        patches.append(f"### {f['filename']}\n{patch}")
    return "\n\n".join(patches)

def ask_claude(diff):
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        print("ERROR: ANTHROPIC_API_KEY secret is missing or empty!")
        sys.exit(1)

    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": (
                    "You are a senior code reviewer. Review the following "
                    "PR diff and give clear, constructive feedback.\n\n"
                    "Focus on: bugs, security issues, ML best practices, "
                    "performance, and readability.\n\n"
                    + diff
                )
            }
        ]
    }

    body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "User-Agent": "claude-reviewer"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
        return data["content"][0]["text"]
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"Claude API error {e.code}: {body}")
        sys.exit(1)

def post_comment(review):
    repo   = os.environ["GITHUB_REPOSITORY"]
    pr_num = os.environ["PR_NUMBER"]
    token  = os.environ["GITHUB_TOKEN"]
    url    = f"https://api.github.com/repos/{repo}/issues/{pr_num}/comments"
    body   = json.dumps({
        "body": f"## 🤖 Claude Code Review\n\n{review}"
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "claude-reviewer"
    }, method="POST")
    with urllib.request.urlopen(req) as r:
        print(f"Comment posted! Status: {r.status}")

if __name__ == "__main__":
    print("Fetching PR diff...")
    diff = get_pr_diff()
    print(f"Got diff ({len(diff)} chars). Sending to Claude...")
    review = ask_claude(diff)
    print("Got review. Posting comment...")
    post_comment(review)
    print("Done!")
