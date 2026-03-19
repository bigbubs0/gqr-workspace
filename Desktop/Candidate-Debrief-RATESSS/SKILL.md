# Candidate-Debrief-RATESSS Skill

## Overview
This Claude Skill implements the proprietary RATESSS methodology for conducting professional candidate debriefs following client interviews. The skill ensures consistent execution of the complex debriefing process, which is critical for maximizing offer acceptance rates and maintaining candidate control throughout the recruiting process.

## Core Principle
**The candidate should spend 75% of the call communicating information to the recruiter.**

## Workflow Structure

### Phase 1: Structured Data Elicitation (RATESSS)
Follow the RATESSS framework systematically to gather complete candidate feedback. Consult `references/RATESSS_framework.md` for detailed questions and techniques.

**Sequential Order:**
1. **R – Relationships**: Gather impressions of role, company, and individuals met
2. **A – Alternatives**: Identify red flags, lingering questions, and competing processes
3. **T – Timeline**: Understand progression of other interviews and availability
4. **E – Expectations**: Clarify compensation, title, and career expectations
5. **S – Sign off**: Identify decision influencers and test commitment level
6. **S – Sell**: Reinforce positives and candidate's value proposition
7. **S – Steps/Strategy**: Confirm interest and establish next steps

### Phase 2: Data Structuring
Organize gathered information into:
- **Positive indicators**: Interest signals, enthusiasm, favorable impressions
- **Red flags/concerns**: Hesitations, competing offers, unresolved questions
- **Action items**: Next steps, information needed, timeline commitments

### Phase 3: Output Generation
Generate two distinct outputs using templates in `assets/`:

1. **Client Feedback Email** (`assets/Client_Feedback_Template.md`)
   - Full paragraph format
   - Reassure client of candidate interest
   - Include impressions of individuals met
   - Flag candidate's standing in other processes
   - Professional, measured tone

2. **Internal Red Flags Note** (`assets/Internal_Red_Flags.md`)
   - Bullet format acceptable
   - Document all concerns and hesitations
   - Note unresolved questions
   - Flag any pushback for Account Manager

### Phase 4: Quality Control
Before finalizing outputs:
- Verify all RATESSS elements were addressed
- Confirm 75% of conversation focused on positives
- Check that softeners were used appropriately
- Validate professional tone (consult `references/Communication_Rules.md`)
- Optional: Run `scripts/tone_validator.py` for objective analysis

## Handling Objections

### Minor Hesitancies
Consult `references/RATESSS_Soft_Rebuttals.md` for:
- Acknowledge before rebutting technique
- Minimize and sidestep strategies
- Positive reinforcement methods

### Major Objections
Consult `references/Hard_Closes.md` for:
- Casino Close (probability and logic)
- Sunk Funds Close (past investment)
- Professional Authority Close (directive)

## Success Criteria
✓ All RATESSS elements captured
✓ Client feedback email demonstrates candidate interest
✓ Internal notes flag all concerns for AM
✓ Communication maintains professional, measured tone
✓ Candidate commits to next steps
✓ Positive momentum toward second interview maintained

## Usage Instructions
1. Begin debrief immediately after candidate's interview
2. Follow RATESSS sequence without deviation
3. Apply soft rebuttals as needed for minor concerns
4. Generate both required outputs before ending conversation
5. Validate quality using communication rules and optional scripts

## File Structure
```
Candidate-Debrief-RATESSS/
├── SKILL.md (this file)
├── references/
│   ├── RATESSS_framework.md
│   ├── RATESSS_Soft_Rebuttals.md
│   ├── Hard_Closes.md
│   └── Communication_Rules.md
├── assets/
│   ├── Client_Feedback_Template.md
│   └── Internal_Red_Flags.md
└── scripts/
    ├── tone_validator.py
    └── completeness_checker.py
```

---
*This skill transforms the RATESSS methodology from static knowledge into an executable, consistent workflow that ensures professional candidate management at every interaction.*
