import re

with open(r"C:\Users\86132\.claude\projects\D--Project-PythonProject-Sumi-Kara\b5913569-c53f-4a17-98ce-fcb6a80b3b25\tool-results\bef8146.txt", "r", encoding="utf-8") as f:
    content = f.read()

# 提取所有GitHub仓库链接
urls = re.findall(r'https://github\.com/([a-zA-Z0-9-]+/[a-zA-Z0-9_.-]+)', content)
unique_repos = sorted(set(urls))

# 过滤掉一些无效的
valid_repos = []
skip_patterns = ['README', 'wiki', 'issues', 'pulls', 'actions', 'releases', 'tree', 'blob', 'commits']
for repo in unique_repos:
    if any(p in repo.lower() for p in skip_patterns):
        continue
    # 跳过awesome-mcp-servers自己
    if 'punkpeye/awesome-mcp-servers' in repo:
        continue
    valid_repos.append(repo)

print(f"总共找到 {len(valid_repos)} 个唯一仓库\n")

# 按类别分组
for i, repo in enumerate(valid_repos, 1):
    print(f"{i}. {repo}")
