# Skill: CV Scorer

## Purpose
Score inbound CVs against active job orders.

## Scoring Rubric (1-10)
| Factor | Weight | Criteria |
|--------|--------|----------|
| Degree | 25% | MD/PhD = 10, PharmD = 7, MS = 5, BS = 3 |
| Clinical Dev Years | 25% | 15+ = 10, 10-14 = 8, 5-9 = 6, <5 = 3 |
| Therapeutic Area Match | 20% | Exact match = 10, adjacent = 6, unrelated = 2 |
| Leadership Level | 15% | C-suite = 10, VP = 8, Director = 6, Manager = 4 |
| FDA Experience | 15% | NDA/BLA lead = 10, submission team = 7, none = 2 |

## Flags (auto-flag these)
- Currently at top-20 pharma
- Prior FDA submission experience (NDA, BLA, IND)
- CMO-track trajectory
- PV/Drug Safety background
- Rare disease or oncology specialization

## Output Format
| Name | LinkedIn | Score | Rationale |
|------|----------|-------|-----------|
| Jane Doe | linkedin.com/in/janedoe | 8.5 | MD, 12yr clinical dev, oncology, NDA lead at Genentech |

Save scored CVs to `/recruiting/candidates/`
