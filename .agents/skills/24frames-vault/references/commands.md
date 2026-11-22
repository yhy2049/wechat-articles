# 常用命令

```bash
cd "$HOME/Documents/24帧运营库"

# 健康检查
python3 00_系统/agent/vault-lint.py
python3 00_系统/agent/vault-lint.py --file "02_项目/苏宁影城路演合作/苏宁影城路演合作.md"

# 重建索引与首页
python3 00_系统/agent/vault-index.py
python3 00_系统/agent/vault-home.py
python3 00_系统/agent/vault-index.py --check
python3 00_系统/agent/vault-home.py --check

# 检索
python3 00_系统/agent/vault-search.py --build
python3 00_系统/agent/vault-search.py "资金 分工" --limit 10

# 健康快照
python3 00_系统/agent/vault-metrics.py --markdown

# 最近日志
grep '^## \[' 00_系统/_changelog.md | tail -5
```
