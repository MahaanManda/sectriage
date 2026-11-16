# sectriage
LLM agent that triages security alerts using RAG over MITRE ATT&amp;CK and incident-response playbooks, with an evaluation harness.


## Evaluation notes

Results and the reasoning behind any label change are recorded rather than hidden.

- **A038 relabeled (2026-11-16).** The alert was written before the Harbor Logistics policy documents existed, and the policy contradicted its label (non-`adm_` account, Wednesday, ticket not in the change register). The policy is the source of truth, so the label changed from benign to true_positive / remote_services / high. The alert text and the model predictions were not touched; saved predictions were re-scored with `python eval.py --rescore`. The relabel moves RAG and the agent up by one alert, because only they have the policy. Before and after numbers are in [data/LABEL_CHANGES.md](data/LABEL_CHANGES.md).
- The Harbor Logistics documents and the 26 hard alerts (`data/alerts_hard.json`) are fictional and were written with Claude's help, with labels fixed before any model run.
