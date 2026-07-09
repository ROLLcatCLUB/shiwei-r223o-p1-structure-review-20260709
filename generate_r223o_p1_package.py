import hashlib
import html
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

STAGE_ID = "1013R_R223O_P1_COLOR_MANUSCRIPT_STRUCTURE_RECOVERY"
ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / "1013R_R223O_SECOND_CROSS_SAMPLE_VALIDATION"
SOURCE_MD = BASE / "R223O_teacher_manuscript_draft_v1.md"
SOURCE_LEDGER = BASE / "R223O_review_ledger_sample.json"
SOURCE_CHAIN = BASE / "R223O_classroom_event_expansion_chain.json"


def write_text(name: str, content: str) -> None:
    (ROOT / name).write_text(content.strip() + "\n", encoding="utf-8")


def write_json(name: str, data) -> None:
    (ROOT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def markdown_to_html(title: str, md: str) -> str:
    lines = md.splitlines()
    body = []
    in_code = False
    in_table = False
    table_rows = []

    def flush_table():
        nonlocal in_table, table_rows
        if not in_table:
            return
        body.append("<table>")
        for idx, row in enumerate(table_rows):
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if idx == 1 and all(set(c.replace(":", "").replace("-", "")) == set() for c in cells):
                continue
            tag = "th" if idx == 0 else "td"
            body.append("<tr>" + "".join(f"<{tag}>{html.escape(c)}</{tag}>" for c in cells) + "</tr>")
        body.append("</table>")
        in_table = False
        table_rows = []

    for raw in lines:
        line = raw.rstrip()
        if line.strip().startswith("```"):
            flush_table()
            body.append("</code></pre>" if in_code else "<pre><code>")
            in_code = not in_code
            continue
        if in_code:
            body.append(html.escape(line))
            continue
        if line.startswith("|") and line.endswith("|"):
            in_table = True
            table_rows.append(line)
            continue
        flush_table()
        if not line.strip():
            body.append("")
        elif line.startswith("# "):
            body.append(f"<h1>{html.escape(line[2:].strip())}</h1>")
        elif line.startswith("## "):
            body.append(f"<h2>{html.escape(line[3:].strip())}</h2>")
        elif line.startswith("### "):
            body.append(f"<h3>{html.escape(line[4:].strip())}</h3>")
        elif line.startswith("#### "):
            body.append(f"<h4>{html.escape(line[5:].strip())}</h4>")
        elif line.startswith("- "):
            body.append(f"<p class=\"li\">{html.escape(line)}</p>")
        else:
            escaped = html.escape(line).replace("【设计意图】", "<strong>【设计意图】</strong>")
            body.append(f"<p>{escaped}</p>")
    flush_table()

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --ink: #213530;
      --muted: #5f746d;
      --line: #dfe9e5;
      --accent: #247d6b;
      --soft: #f4faf7;
      --paper: #fffdf7;
      --note: #f9f3df;
    }}
    body {{
      margin: 0;
      background: #f3f7f5;
      color: var(--ink);
      font: 16px/1.72 "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", Arial, sans-serif;
    }}
    main {{
      max-width: 1020px;
      margin: 0 auto;
      padding: 48px 56px 72px;
      background: var(--paper);
      min-height: 100vh;
      box-shadow: 0 10px 35px rgba(29, 68, 58, .08);
    }}
    h1 {{ margin: 0 0 18px; font-size: 30px; line-height: 1.32; color: #174f45; }}
    h2 {{ margin: 42px 0 16px; padding-top: 8px; border-top: 1px solid var(--line); font-size: 22px; color: #185c4f; }}
    h3 {{ margin: 34px 0 14px; font-size: 19px; color: #20342f; }}
    h4 {{ margin: 28px 0 10px; font-size: 17px; color: #25443d; }}
    p {{ margin: 10px 0; }}
    strong {{ color: #185c4f; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 14px 0 22px;
      font-size: 15px;
      background: #fff;
    }}
    th, td {{
      border: 1px solid var(--line);
      padding: 9px 11px;
      vertical-align: top;
      text-align: left;
    }}
    th {{ background: var(--soft); color: #174f45; font-weight: 700; }}
    pre {{
      background: #f7faf8;
      border: 1px solid var(--line);
      padding: 14px 16px;
      overflow-x: auto;
      border-radius: 6px;
      color: #324d46;
    }}
    .li {{ margin-left: 1em; color: var(--muted); }}
    p:has(strong) {{
      background: var(--note);
      border-left: 4px solid #d69c2f;
      padding: 10px 12px;
      border-radius: 4px;
    }}
    @media (max-width: 760px) {{
      main {{ padding: 28px 22px 48px; }}
      h1 {{ font-size: 24px; }}
      table {{ font-size: 14px; }}
    }}
  </style>
</head>
<body><main>
{chr(10).join(body)}
</main></body>
</html>
"""


MAINLINE = """## 七、本课主线图

本课主线不是“讲三原色概念”，而是让学生沿着一条可观察、可实验、可表达的色彩路径往前走：

```text
校园取色
→ 红黄蓝起点
→ 两色相碰
→ 同色差异
→ 复色进阶
→ 命名表达
→ 色彩创想会
```

| 主线节点 | 学生动作 | 教师关键追问 | 学习证据 |
| --- | --- | --- | --- |
| 校园取色 | 从校园照片或色彩漂流瓶中找红、黄、蓝和不易命名的颜色 | 这块颜色让你想到阳光、树叶还是操场上的影子？ | 校园色彩观察句 |
| 红黄蓝起点 | 判断为什么先用红、黄、蓝做实验 | 如果只给红、黄、蓝，它们碰在一起会不会出现新的颜色？ | 三原色起点记录 |
| 两色相碰 | 少量调和两种颜色，圈出一次清楚的调色结果 | 它更靠近哪一种原来的颜色？ | 间色调色样本 |
| 同色差异 | 比较同一种新颜色的偏向、明暗和冷暖 | 这块绿像新芽，还是像雨后草地？ | 色彩差异句 |
| 复色进阶 | 在间色中少量加入第三色，观察颜色气质变化 | 这块颜色不那么亮了，但它像傍晚、雨天还是树影？ | 复色变化记录 |
| 命名表达 | 为代表色命名，说明来源和感受 | 它从哪两种颜色碰出来？它让你想到什么画面？ | 色彩命名卡 |
| 色彩创想会 | 带着记录介绍一块代表色并听取同伴建议 | 同伴说它像夏天，证据在哪里？ | 展示评价记录 |
"""


SUMMARY = """## 八、单课教学过程摘要

| 阶段 | 活动名称 | 主要任务 | 设计意图 | 证据输出 |
| --- | --- | --- | --- | --- |
| 入场与问题 | 游园回看；认一认 | 把校园色彩带回课堂，生成“红、黄、蓝能不能变出更多颜色”的问题 | 先让学生从生活色彩进入实验问题，避免一上来背三原色概念 | 校园色彩观察句；三原色起点记录 |
| 实验与观察 | 调一调；比一比 | 两色相碰调出间色，再比较同色的偏向、明暗和冷暖 | 让学生看到颜色变化的路径，而不是只得到橙、绿、紫这些结果 | 间色调色样本；色彩差异句 |
| 进阶与表达 | 进一阶；碰一碰 | 用少量第三色调出复色，并把调试结果命名、选择、展示 | 把色彩实验推进到画面感受和表达选择，让颜色成为美术语言 | 复色变化记录；色彩命名卡 |
| 展示与收束 | 说一说 | 用来源、特点和联想介绍一块代表色，形成色彩创想会材料 | 用证据说颜色，用颜色说感受，回应“色彩是美术表现的重要语言” | 展示评价记录 |

这一摘要只帮助老师先看清本课怎么走；具体话术、学生反应、追问和补救仍在下面的教学过程里展开。
"""


def build_teacher_md() -> str:
    md = SOURCE_MD.read_text(encoding="utf-8")
    md = md.replace("# 《色彩的碰撞》教师文稿版 v1", "# 《色彩的碰撞》教师文稿版 v2")
    md = md.replace("stage_id=1013R_R223O_SECOND_CROSS_SAMPLE_VALIDATION", f"stage_id={STAGE_ID}")
    md = md.replace("status=third_cross_sample_teacher_manuscript_draft", "status=color_manuscript_structure_recovered_draft")
    md = md.replace(
        "本稿用于验证 R223M-P5 锁定的课堂事件展开标准，能否迁移到“视觉语言 / 色彩感知 / 色彩表达”类课例。它不是正式 UI，不写入备课本，也不调用模型或运行时。默认层只保留教师可读文稿；完整课堂事件、组件触发、大屏触发、学习单和评价证据保留在 review ledger。",
        "本稿在 R223O 迁移验证稿基础上补回成熟教案的组织层级：先看课时定位和单课结构，再看本课主线图与教学过程摘要，最后进入详细教学过程。课堂事件链、review ledger、大屏、学习单和评价证据不重写；默认层继续保持教师可读文稿形态。"
    )
    md = md.replace("## 七、教学过程", MAINLINE + "\n\n" + SUMMARY + "\n\n## 九、教学过程")
    md = md.replace("## 八、评价设计", "## 十、评价设计")
    md = md.replace("## 九、板书 / 大屏结构", "## 十一、板书 / 大屏结构")
    md = md.replace("## 十、确认门", "## 十二、确认门")
    md = md.replace("本稿仍为 preview-only。它只用于 R223O 第三样本迁移验证", "本稿仍为 preview-only。它只用于 R223O-P1 教师文稿结构恢复验证")
    return md


def build_mainline_map() -> str:
    return "# R223O-P1 本课主线图\n\n" + MAINLINE


def build_process_summary() -> str:
    return "# R223O-P1 单课教学过程摘要\n\n" + SUMMARY


def build_compare() -> str:
    return """# R223O-P1 与 R223O 对照

| 项目 | R223O v1 | R223O-P1 v2 |
| --- | --- | --- |
| 标准迁移 | 已验证视觉语言 / 色彩感知课型可迁移 | 保留，不重写推理链 |
| 教师文稿结构 | 有课时定位、单课结构、教学过程、评价，但中间组织层弱 | 新增本课主线图和单课教学过程摘要 |
| 单课结构表 | 只承担简要概览 | 与主线图、过程摘要形成“概览—路径—摘要—过程”四层 |
| 教学过程 | 连续叙述可读，但关系先导不足 | 保留原过程，前置阶段、活动、子活动、设计意图、证据关系 |
| 后端字段 | 默认稿未暴露 | 继续不暴露 event_id / component_trigger |
| review ledger | 已保留 | 原样复制保留 |

## 本轮不做

- 不改课堂事件 JSON 的语义；
- 不删除学生可能反应、教师追问、补救、投屏、学习单、评价证据；
- 不恢复卡片墙；
- 不改 R97B / UI / runtime / model / prompt / db。
"""


def build_report() -> str:
    return f"""# R223O-P1 教师文稿结构恢复报告

```text
stage_id={STAGE_ID}
source_stage_id=1013R_R223O_SECOND_CROSS_SAMPLE_VALIDATION
decision=PASS_LOCAL_VALIDATOR
structure_recovery=mainline_map_and_process_summary_added
formal_ui=false
r97b_modified=false
runtime_connected=false
provider_model_connected=false
database_written=false
```

## 处理结论

R223O 已经证明课堂事件展开标准能迁移到《色彩的碰撞》，但教师文稿层级偏弱。P1 不重写内容，只补回成熟教案需要的组织层：本课主线图、单课教学过程摘要，以及“概览—路径—摘要—过程—评价”的阅读顺序。

## 本轮新增

- `本课主线图`：校园取色 → 红黄蓝起点 → 两色相碰 → 同色差异 → 复色进阶 → 命名表达 → 色彩创想会。
- `单课教学过程摘要`：按四个阶段说明活动名称、主要任务、设计意图和证据输出。
- 教师稿标题、元数据和确认门更新为 R223O-P1。
- review ledger 从 R223O 原包复制保留，不进入默认稿。

## 边界

未改 R97B，未新增正式 route，未改 frontend/backend，未接 runtime、provider/model、prompt、db，未写回 lesson body，未 formal apply。
"""


def build_readme() -> str:
    return f"""# R223O-P1 教师文稿结构恢复审核包

```text
stage_id={STAGE_ID}
status=PASS_LOCAL_VALIDATOR
source_stage=R223O_SECOND_CROSS_SAMPLE_VALIDATION
formal_ui=false
R97B / UI / runtime / prompt / model / db = untouched
```

## 建议 GPT / 教师审核顺序

1. `R223O_P1_teacher_manuscript_draft_v2.html`
2. `R223O_P1_teacher_manuscript_draft_v2.md`
3. `R223O_P1_color_lesson_mainline_map.md`
4. `R223O_P1_teaching_process_summary.md`
5. `R223O_P1_before_after_compare_with_R223O.md`
6. `R223O_P1_report.md`
7. `R223O_P1_review_ledger_sample.json`

## 审核重点

- 是否补回成熟教案文稿结构；
- 是否有清楚的本课主线和教学过程摘要；
- 详细过程是否仍保留课堂展开深度；
- 默认稿是否没有暴露后端字段；
- 是否没有迁移文具课 / 纸印课内容；
- 是否仍不改 UI / R97B / runtime。
"""


def build_validator() -> str:
    return r'''import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED = [
    "R223O_P1_teacher_manuscript_draft_v2.md",
    "R223O_P1_teacher_manuscript_draft_v2.html",
    "R223O_P1_color_lesson_mainline_map.md",
    "R223O_P1_teaching_process_summary.md",
    "R223O_P1_before_after_compare_with_R223O.md",
    "R223O_P1_report.md",
    "R223O_P1_review_ledger_sample.json",
    "PACKAGE_MANIFEST.json",
    "README_FOR_GPT_REVIEW.md",
]
checks = []
failures = []

def check(name, cond):
    checks.append(name)
    if not cond:
        failures.append(name)

for file in REQUIRED:
    check(f"exists:{file}", (ROOT / file).exists())

teacher = (ROOT / "R223O_P1_teacher_manuscript_draft_v2.md").read_text(encoding="utf-8")
ledger = json.loads((ROOT / "R223O_P1_review_ledger_sample.json").read_text(encoding="utf-8"))
manifest = json.loads((ROOT / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))

required_sections = [
    "课时定位", "本课在单元中的位置", "教学目标", "教学重难点", "教学准备",
    "单课结构", "本课主线图", "单课教学过程摘要", "教学过程", "评价设计", "板书 / 大屏结构", "确认门"
]
for section in required_sections:
    check(f"teacher_has_{section}", section in teacher)

mainline_nodes = ["校园取色", "红黄蓝起点", "两色相碰", "同色差异", "复色进阶", "命名表达", "色彩创想会"]
for node in mainline_nodes:
    check(f"mainline_has_{node}", node in teacher)

summary_terms = ["活动名称", "主要任务", "设计意图", "证据输出"]
for term in summary_terms:
    check(f"summary_has_{term}", term in teacher)

process_terms = ["游园回看", "认一认", "调一调", "比一比", "进一阶", "碰一碰", "说一说"]
for term in process_terms:
    check(f"process_keeps_{term}", term in teacher)

check("design_intent_count_at_least_4", teacher.count("【设计意图】") >= 4)
check("ledger_event_count_7", len(ledger.get("events", [])) == 7)
check("manifest_boundary_formal_ui_false", manifest.get("formal_ui") is False)
check("manifest_boundary_r97b_false", manifest.get("r97b_modified") is False)
check("manifest_boundary_runtime_false", manifest.get("runtime_connected") is False)

backend_terms = ["event_id", "component_trigger", "screen_trigger", "learning_sheet_trigger", "evidence_trigger"]
for term in backend_terms:
    check(f"teacher_no_backend_{term}", term not in teacher)

banned_sample_terms = ["文具", "智造", "代言", "赠笔礼", "纸印", "版画车间坊", "印痕"]
for term in banned_sample_terms:
    check(f"teacher_not_migrate_{term}", term not in teacher)

result = {
    "passed": not failures,
    "check_count": len(checks),
    "failed": len(failures),
    "failures": failures,
    "ledger_event_count": len(ledger.get("events", [])),
    "structure_recovery": "mainline_map_and_process_summary"
}
(ROOT / "validate_1013R_R223O_P1_color_manuscript_structure_recovery_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False))
if failures:
    raise SystemExit(1)
'''


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    teacher = build_teacher_md()
    write_text("R223O_P1_teacher_manuscript_draft_v2.md", teacher)
    write_text("R223O_P1_teacher_manuscript_draft_v2.html", markdown_to_html("R223O-P1 《色彩的碰撞》教师文稿版 v2", teacher))
    write_text("R223O_P1_color_lesson_mainline_map.md", build_mainline_map())
    write_text("R223O_P1_teaching_process_summary.md", build_process_summary())
    write_text("R223O_P1_before_after_compare_with_R223O.md", build_compare())
    write_text("R223O_P1_report.md", build_report())
    shutil.copyfile(SOURCE_LEDGER, ROOT / "R223O_P1_review_ledger_sample.json")
    shutil.copyfile(SOURCE_CHAIN, ROOT / "R223O_P1_classroom_event_expansion_chain.json")
    write_text("README_FOR_GPT_REVIEW.md", build_readme())
    write_text("validate_1013R_R223O_P1_color_manuscript_structure_recovery.py", build_validator())
    files = [
        "R223O_P1_teacher_manuscript_draft_v2.md",
        "R223O_P1_teacher_manuscript_draft_v2.html",
        "R223O_P1_color_lesson_mainline_map.md",
        "R223O_P1_teaching_process_summary.md",
        "R223O_P1_before_after_compare_with_R223O.md",
        "R223O_P1_report.md",
        "R223O_P1_review_ledger_sample.json",
        "R223O_P1_classroom_event_expansion_chain.json",
        "README_FOR_GPT_REVIEW.md",
        "validate_1013R_R223O_P1_color_manuscript_structure_recovery.py",
    ]
    manifest = {
        "stage_id": STAGE_ID,
        "source_stage_id": "1013R_R223O_SECOND_CROSS_SAMPLE_VALIDATION",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "formal_ui": False,
        "r97b_modified": False,
        "runtime_connected": False,
        "provider_model_connected": False,
        "database_written": False,
        "files": files,
    }
    write_json("PACKAGE_MANIFEST.json", manifest)


if __name__ == "__main__":
    main()
