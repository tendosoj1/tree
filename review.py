# review.py v3
import os, sys, json, urllib.request, urllib.error

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
GITHUB_API    = "https://api.github.com"

def gh_get(path):
    token = os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request(
        f"{GITHUB_API}{path}",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "claude-reviewer"
        }
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

def gh_post(path, data):
    token = os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request(
        f"{GITHUB_API}{path}",
        data=json.dumps(data).encode(),
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
            "User-Agent": "claude-reviewer"
        }
    )
    with urllib.request.urlopen(req) as r:
        return r.status

repo   = os.environ["GITHUB_REPOSITORY"]
pr_num = os.environ["PR_NUMBER"]

print("Fetching PR files...")
files  = gh_get(f"/repos/{repo}/pulls/{pr_num}/files")
diff   = "\n\n".join(
    f"### {f['filename']}\n{f.get('patch','(no diff)')}"
    for f in files
)
print(f"Got {len(files)} file(s).")

print("Calling Claude API...")
api_key = os.environ["ANTHROPIC_API_KEY"]

payload = json.dumps({
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1024,
    "messages": [{
        "role": "user",
        "content": f"Review this code diff and give constructive feedback on bugs, style, and improvements:\n\n{diff}"
    }]
}).encode()

req = urllib.request.Request(
    ANTHROPIC_URL,
    data=payload,
    method="POST",
    headers={
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
)

try:
    with urllib.request.urlopen(req) as r:
        result = json.loads(r.read().decode())
    review = result["content"][0]["text"]
    print("Got Claude review!")
except urllib.error.HTTPError as e:
    err = e.read().decode()
    print(f"Claude API failed: {e.code} - {err}")
    sys.exit(1)

print("Posting comment to PR...")
status = gh_post(
    f"/repos/{repo}/issues/{pr_num}/comments",
    {"body": f"## 🤖 Claude Code Review\n\n{review}"}
)
print(f"Done! GitHub status: {status}")
