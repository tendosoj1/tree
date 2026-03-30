import os, sys, json, urllib.request, urllib.error

repo   = os.environ["GITHUB_REPOSITORY"]
pr_num = os.environ["PR_NUMBER"]
token  = os.environ["GITHUB_TOKEN"]
key    = os.environ["ANTHROPIC_API_KEY"]

req = urllib.request.Request(
    f"https://api.github.com/repos/{repo}/pulls/{pr_num}/files",
    headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json", "User-Agent": "bot"}
)
with urllib.request.urlopen(req) as r:
    files = json.loads(r.read().decode())

diff = "\n\n".join(f"### {f['filename']}\n{f.get('patch','no diff')}" for f in files)
print("Got diff, calling Claude...")

body = json.dumps({
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": f"Review this code diff:\n\n{diff}"}]
}).encode()

req2 = urllib.request.Request(
    "https://api.anthropic.com/v1/messages",
    data=body,
    method="POST",
    headers={
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
)

try:
    with urllib.request.urlopen(req2) as r:
        review = json.loads(r.read().decode())["content"][0]["text"]
    print("Got review!")
except urllib.error.HTTPError as e:
    print(f"FAILED: {e.code} {e.read().decode()}")
    sys.exit(1)

body2 = json.dumps({"body": f"## 🤖 Claude Review\n\n{review}"}).encode()
req3 = urllib.request.Request(
    f"https://api.github.com/repos/{repo}/issues/{pr_num}/comments",
    data=body2,
    method="POST",
    headers={"Authorization": f"token {token}", "Content-Type": "application/json", "User-Agent": "bot"}
)
urllib.request.urlopen(req3)
print("Done!")
