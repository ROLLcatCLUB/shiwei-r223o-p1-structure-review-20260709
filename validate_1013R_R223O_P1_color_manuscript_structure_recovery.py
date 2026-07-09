import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED = [
    "R223O_P1_teacher_manuscript_draft_v2.md",
    "R223O_P1_teacher_manuscript_draft_v2.html",
    "R223O_P1_color_lesson_mainline_map.md",
    "R223O_P1_teaching_process_summary.md",
    "R223O_P1_before_after_compare_with_R223O.md",
    "R223O_P1_report.md",
    "R223O_P1_browser_smoke_result.json",
    "R223O_P1_teacher_manuscript_draft_v2_screenshot.png",
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
smoke = json.loads((ROOT / "R223O_P1_browser_smoke_result.json").read_text(encoding="utf-8"))

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
check("browser_smoke_has_mainline", smoke.get("hasMainlineMap") is True)
check("browser_smoke_has_summary", smoke.get("hasProcessSummary") is True)
check("browser_smoke_has_nodes", smoke.get("hasMainlineNodes") is True)
check("browser_smoke_no_backend_terms", smoke.get("hasBackendTerms") is False)
check("browser_smoke_no_wenju_migration", smoke.get("hasMigratedWenju") is False)
check("browser_smoke_no_paper_print_migration", smoke.get("hasMigratedPaperPrint") is False)
check("browser_smoke_no_overflow", smoke.get("pageOverflow") is False)

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
