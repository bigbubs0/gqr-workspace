# Candidate Control Skill
## Complete Recruitment Automation System for CLABVISSS & RATESSS

---

## Overview

The Candidate Control Skill is a comprehensive Claude AI skill package that automates and standardizes the multi-step recruitment process from initial candidate intake through post-interview feedback. It ensures consistent data capture, professional communication, and candidate control throughout the hiring workflow.

### Key Features

✅ **Systematic Candidate Intake** - CLABVISSS framework for comprehensive data collection  
✅ **Automated CV Submissions** - Generate client-ready emails with internal notes  
✅ **Structured Interview Debriefs** - RATESSS framework for post-interview feedback  
✅ **Professional Communication** - Maintain firm standards and tone guidelines  
✅ **Quality Control** - Built-in validation checklists for every output  

---

## What's Included

```
Candidate-Control-Skill/
├── SKILL.md                                    # Master workflow & instructions
├── references/
│   ├── CLABVISSS-framework.md                 # Complete intake methodology
│   ├── RATESSS-framework.md                   # Complete debrief methodology
│   └── communication-rules.md                 # Email standards & tone guidelines
├── assets/
│   ├── cv-submission-template.md              # CV submission email formats
│   └── client-feedback-template.md            # Client feedback email formats
└── scripts/
    └── validation-checklist.md                # Quality control checklists
```

---

## Quick Start Guide

### Option 1: Full Skill Upload (Recommended)

1. **Upload all files** to a new Claude conversation
2. **Say:** "Use the Candidate-Control-Skill to guide me through a candidate intake"
3. **Follow along** as Claude systematically walks you through the process

### Option 2: Use in a Claude Project

1. **Create a new Project** in Claude
2. **Add `SKILL.md`** to the Project's custom instructions
3. **Upload reference files** to Project knowledge
4. Every conversation in this Project will automatically use the skill

### Option 3: Selective Usage

Upload only the files you need:
- **Just intake?** → Upload `SKILL.md` + `CLABVISSS-framework.md`
- **Just debrief?** → Upload `SKILL.md` + `RATESSS-framework.md`
- **Just templates?** → Upload the specific template from `assets/`

---

## How to Use

### Phase 1: Candidate Intake (CLABVISSS)

**Start the intake:**
```
"Let's conduct a CLABVISSS intake for a [position] candidate."
```

Claude will systematically guide you through collecting:
- **C**ommitment & Flexibility
- **L**ocation Preferences
- **A**vailability & Timeline
- **B**ackground Verification
- **V**isa & Work Authorization
- **I**deal vs. Acceptable Role
- **S**alary & Compensation
- **S**tart Date Flexibility
- **S**tage in Other Processes

**Duration:** 15-30 minutes  
**Output:** Complete candidate profile with all decision-making data

---

### Phase 2: CV Submission Email

**Generate the email:**
```
"Generate the CV submission email based on the intake data."
```

Claude will create:
- **BLACK TEXT** - Client-ready content (copy-paste without editing)
- **RED TEXT** - Internal notes for Account Manager (never sent to client)

**Output includes:**
- Professional candidate summary
- 2-3 tailored selling points
- Motivations for change
- Interest in THIS specific company
- Complete internal notes with red flags, compensation, competing processes, closing strategy

---

### Phase 3: Interview Debrief (RATESSS)

**Start the debrief:**
```
"Let's conduct a RATESSS debrief for the candidate's interview."
```

Claude will systematically collect:
- **R**elationships Formed
- **A**lternatives & Other Opportunities
- **T**imeline Updates
- **E**xpectations (Changed or Confirmed)
- **S**ign Off & Buy-In Level
- **S**ell Points (What Impressed Them)
- **S**teps & Strategy Going Forward

**Timing:** Within 2 hours of candidate's interview  
**Duration:** 15-20 minutes

---

### Phase 4: Client Feedback Email

**Generate the feedback:**
```
"Create the client feedback email from the debrief."
```

Claude will create:
- **CLIENT EMAIL** - Positive, reassuring summary of interview feedback
- **INTERNAL NOTES** - Complete documentation of concerns, hesitations, closing strategy

**Output includes:**
- Overall candidate enthusiasm
- Specific interviewer feedback
- Competitive positioning (where you rank)
- Interest level confirmation
- Internal concerns and risk factors
- Detailed closing strategy

---

## Example Workflow

```
You: "I need to do a CLABVISSS intake for a Senior Product Manager candidate."

Claude: "Let's begin the candidate intake process using the CLABVISSS framework. 
I'll ask you one question at a time to gather comprehensive information.

First, let's understand their current search status and commitment level. 
Are they actively interviewing with other companies right now?"

You: "Yes, they're in final rounds with two companies."

Claude: "Got it. Can you tell me specifically which companies and what stage 
they're at in each process?"

[Conversation continues through all CLABVISSS points...]

Claude: "Perfect. I now have all the information needed. Here's your CV submission 
email with client-ready content and internal notes..."

[Claude generates complete formatted email with BLACK TEXT and RED TEXT sections]
```

---

## Key Features & Benefits

### Ensures Complete Data Capture
- No missed information or vague answers
- Systematic questioning prevents oversight
- Built-in prompts to probe deeper when needed

### Maintains Professional Standards
- Consistent tone and formatting
- Adheres to firm communication guidelines
- Clear separation of client vs. internal information

### Saves Time
- Automated email generation
- Pre-formatted templates
- No manual formatting needed

### Improves Candidate Control
- Structured approach maintains engagement
- Clear understanding of commitment level
- Competitive landscape visibility

### Reduces Risk
- Red flags surfaced early
- Concerns documented internally
- Strategic recommendations provided

---

## Best Practices

### During Intake or Debrief

1. **Take your time** - Don't rush through questions
2. **Probe for specifics** - Vague answers should trigger follow-ups
3. **Let candidate talk** - They should do 75% of talking
4. **Capture quotes** - Exact language helps in emails later
5. **Note red flags immediately** - Don't forget concerns

### When Generating Emails

1. **Review the output** - Always check for accuracy
2. **Customize if needed** - Add specific details Claude might not capture
3. **Use validation checklist** - Reference `scripts/validation-checklist.md`
4. **Verify names/dates** - Double-check all proper nouns and numbers
5. **Separate BLACK/RED clearly** - Never send RED TEXT to clients

### General Tips

- **Use early in relationship** - CLABVISSS works best at first substantive conversation
- **Call within 2 hours** - RATESSS is most effective immediately after interview
- **Be consistent** - Use the same framework for every candidate
- **Give feedback** - Note what works and what doesn't to refine over time
- **Trust the process** - The frameworks are designed to be comprehensive

---

## File Reference Guide

### SKILL.md
**Purpose:** Master workflow document  
**When to use:** Primary instruction file for Claude  
**Contains:** Complete process from intake through feedback

### CLABVISSS-framework.md
**Purpose:** Detailed intake methodology  
**When to use:** Reference during candidate intake conversations  
**Contains:** All 9 components with questions, data points, red flags

### RATESSS-framework.md
**Purpose:** Detailed debrief methodology  
**When to use:** Reference during post-interview debrief calls  
**Contains:** All 7 components with questions, data points, best practices

### communication-rules.md
**Purpose:** Email standards and tone guidelines  
**When to use:** Reference when reviewing generated emails  
**Contains:** Format rules, tone guidelines, examples, common mistakes

### cv-submission-template.md
**Purpose:** Format guide for CV submission emails  
**When to use:** Reference for proper email structure  
**Contains:** Templates, examples, component breakdowns

### client-feedback-template.md
**Purpose:** Format guide for client feedback emails  
**When to use:** Reference for proper feedback structure  
**Contains:** Templates, examples, scenario variations

### validation-checklist.md
**Purpose:** Quality control checklist  
**When to use:** Before sending any output to Account Manager  
**Contains:** Complete validation process, common mistakes, approval criteria

---

## Customization

This skill can be customized for your firm's specific needs:

### Easy Customizations

- **Add/remove CLABVISSS components** - Tailor to your intake priorities
- **Modify email templates** - Match your firm's style
- **Adjust tone guidelines** - Align with your communication preferences
- **Update validation criteria** - Add firm-specific quality checks

### How to Customize

1. **Edit the relevant .md file** in a text editor
2. **Save changes** to the file
3. **Re-upload to Claude** - The updated version will be used

### Maintain Version Control

- Keep original files as backups
- Document changes in file header
- Test modifications before full rollout

---

## Troubleshooting

### Claude isn't following the framework

**Solution:** Make sure you've uploaded `SKILL.md` and reference files. Explicitly say "Use the Candidate-Control-Skill" to activate.

### Generated emails are too generic

**Solution:** Provide more specific details during intake/debrief. Claude can only work with the information you give.

### Output is missing RED TEXT section

**Solution:** Explicitly ask "Include internal notes" or reference the `cv-submission-template.md` to remind Claude of the structure.

### Candidate answers are vague

**Solution:** Use the probing questions in the framework files. Don't accept "I'm flexible" - push for specifics.

### Quality isn't consistent

**Solution:** Use the `validation-checklist.md` before every send. Create a habit of reviewing all outputs.

---

## Support & Feedback

### Getting Help

- **Review framework files** - Most answers are in the detailed methodology docs
- **Check templates** - See examples of good outputs
- **Use validation checklist** - Catch common issues before they become problems

### Providing Feedback

As you use this skill, note:
- What works well
- What could be improved
- Edge cases or scenarios not covered
- Suggestions for additional features

Use this feedback to refine and improve the skill over time.

---

## Advanced Usage

### Combining with Other Tools

This skill works well alongside:
- **CRM systems** - Copy data directly into your tracking system
- **Email templates** - Use generated content in your email platform
- **ATS platforms** - Document complete candidate profiles
- **Calendaring tools** - Schedule follow-ups based on timelines

### Batch Processing

For multiple candidates:
1. Complete intake for Candidate A
2. Ask Claude to "save this data and start a new intake"
3. Complete intake for Candidate B
4. Generate emails for both at the end

### Training New Recruiters

Use this skill as a training tool:
- Walk new hires through the frameworks
- Show them examples of good vs. poor outputs
- Have them practice intake with supervision
- Review their generated emails against validation checklist

---

## Version Information

**Current Version:** 1.0  
**Last Updated:** October 2025  
**Created By:** Based on CLABVISSS and RATESSS methodologies  

---

## License & Usage

This skill package is designed for internal use within your recruitment organization. Customize and adapt as needed for your specific workflows and requirements.

---

**Ready to get started? Upload the skill files to Claude and begin your first candidate intake!**
