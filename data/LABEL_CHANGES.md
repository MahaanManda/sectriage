# Label changes

Labels are changed only when they contradict the source of truth. Each change is listed here with the reason and the effect on the eval numbers. The old label is kept inside the alert record under `label_revision`.

## 2026-11-16: A038 (data/alerts.json)

- **Before:** benign / benign / informational. "Known admin, known source, approved change and window."
- **After:** true_positive / remote_services / high.
- **Reason:** A038 was written before the Harbor Logistics policy documents existed. Those documents (the source of truth) contradict it: `tech_rivera` is not an `adm_` account, patching runs Sundays 01:00 to 05:00 UTC from JUMP01 (this alert is a Wednesday from ADM-01), and CHG-1050 is not in the change register.
- **Severity assumption:** High assumes the 20 servers include Tier 1 assets. The alert does not list them. If they were all Tier 2 the policy would give Medium.
- **Alert text and model predictions were not changed.** Saved predictions were re-scored with `python eval.py --rescore`, with no new API calls.

Effect on the 40-alert set (knowledge base with org documents):

| mode | verdict | category | severity | false alarms | missed threats |
|---|---|---|---|---|---|
| baseline, before | 100% | 90% | 95% | 0 | 0 |
| baseline, after | 98% | 88% | 92% | 0 | 1 |
| RAG, before | 97.5% | 90% | 95% | 1 | 0 |
| RAG, after | 100% | 92% | 98% | 0 | 0 |
| agent, before | 97.5% | 85% | 95% | 1 | 0 |
| agent, after | 100% | 88% | 98% | 0 | 0 |

"Before" baseline is from the run with the 20-document knowledge base (`eval_results/easy_kb20`); baseline does not use the knowledge base, so it is unaffected by it. Before and after RAG/agent numbers are in `eval_results/easy/summary_before_A038_relabel.json` and `eval_results/easy/summary.json`.

Note that this relabel moves the numbers in RAG's favor by exactly one alert, because only the models with the policy documents can know the correct answer. It was made because the label contradicted the policy, not to change the result, but the one-alert effect should be read with that in mind.
