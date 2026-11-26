#!/usr/bin/env python3
"""离线回放：不联网、不调模型，展示一轮请求的决策链路。

数据来自 74 轮真实运行日志的脱敏摘录（data/sample_runs.json）。
运行：python3 demo.py            # 列出全部
     python3 demo.py 0          # 看第 0 条
"""
import json
import sys
from pathlib import Path

DATA = Path(__file__).parent / "data" / "sample_runs.json"


def rule(title):
    print(f"\n{'─' * 62}\n{title}\n{'─' * 62}")


def show(run: dict, idx: int):
    rule(f"[{idx}] 输入")
    if run.get("note"):
        print(f"※ {run['note']}\n")
    print(run["question"])

    rule("① 问题理解（规则 + 模型结构化）")
    i = run["intake"]
    print(f"领域      {i['legal_domain']}")
    print(f"任务目标  {'、'.join(i['task_goals'] or []) or '—'}")
    print(f"已知事实  {' / '.join((i['known_facts'] or [])[:3]) or '—'}")
    print(f"缺失信息  {' / '.join((i['missing_facts'] or [])[:3]) or '—'}")
    print(f"提问立场  {i['user_side'] or '—'}")

    rule("② 技能规划（BM25 召回 + 规则表排序，上限 3 步）")
    for n, p in enumerate(run["plan"], 1):
        flag = "需检索" if p.get("requires_mcp") else "不检索"
        print(f"{n}. {p['name']:<26} [{flag}]  {p['reason']}")
    if not run["plan"]:
        print("（本轮不规划技能）")

    rule("③ 执行（工具调用）")
    print(f"门控结论：{'允许调用付费检索' if run['mcp_required'] else '不调用检索'}")
    for t in run["tool_calls"]:
        print(f"→ {t['tool']}\n   参数 {t['args']}")
    if not run["tool_calls"]:
        print("（未调用工具）")

    rule("④ 校验与落盘")
    v = run["validation"]
    print(f"该查是否真查   {v.get('mcp_called_when_required')}")
    print(f"回答被截断     {v.get('answer_truncated')}")
    print(f"本轮耗时       {run['elapsed_s']} s")

    rule("⑤ 输出（摘录）")
    print(run["answer_excerpt"].strip()[:420] + " …")


def main():
    runs = json.loads(DATA.read_text(encoding="utf-8"))
    if len(sys.argv) > 1:
        show(runs[int(sys.argv[1])], int(sys.argv[1]))
        return
    print(f"共 {len(runs)} 条脱敏样例。用法：python3 demo.py <序号>\n")
    for n, r in enumerate(runs):
        need = "需检索" if r["mcp_required"] else "不检索"
        skills = "、".join(p["name"] for p in r["plan"]) or "—"
        mark = " ⚠️" if r.get("note","").startswith("**") else ""
        print(f"[{n}] [{need}] {r['question'][:34]}…  → {skills}{mark}")


if __name__ == "__main__":
    main()
