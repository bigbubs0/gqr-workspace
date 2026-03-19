import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_client():
    return OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

EXTRACTION_PROMPT = """You are an AI assistant helping a biotech/pharma executive recruiter extract structured information from candidate interview notes or transcripts.

CONTEXT: The recruiter focuses on clinical development roles (VPs, Directors, Medical Directors) in biotech/pharma. Key things that matter:
- Big Pharma → Biotech transitions (highly valued)
- Phase progression experience (especially Phase 2+)
- Power companies: Amgen, Genentech, BMS, Pfizer, Regeneron, Vertex, Gilead
- Therapeutic area depth (oncology, rare disease, immunology, CNS)
- Regulatory experience (FDA meetings, IND filings, breakthrough designations)
- Team building from scratch

RED FLAGS TO DETECT:
- Jobs held for less than 1 year (unless contractor role or known layoff)
- Compliance/regulatory issues mentioned
- Unrealistic compensation expectations (>30% jump without justification)
- Location inflexibility when role requires relocation
- Vague about accomplishments or technical details

Extract the following information from the interview notes/transcript and return ONLY valid JSON:

{
  "name": "Full name",
  "current_company": "Current employer",
  "current_title": "Current job title",
  "years_experience_total": <number>,
  "years_experience_therapeutic": <number or null>,
  "technical_skills": ["IND filings", "Phase 2 trials", "Oncology", etc.],
  "compensation_current_min": <number or null>,
  "compensation_current_max": <number or null>,
  "compensation_target_min": <number or null>,
  "compensation_target_max": <number or null>,
  "notice_period": "2 weeks / 1 month / etc.",
  "location": "City, State",
  "open_to_relocation": true/false,
  "red_flags": "Comma-separated list of concerns, or empty string if none",
  "why_interesting": "3-sentence narrative about why this candidate stands out, focusing on clinical development trajectory, power company experience, therapeutic depth, and cultural fit signals",
  "therapeutic_areas": ["oncology", "rare disease", etc.],
  "phase_experience": ["Preclinical", "Phase 1", "Phase 2", "Phase 3", "NDA/BLA"]
}

IMPORTANT INSTRUCTIONS:
- For compensation ranges (e.g., "$180-200K"), capture BOTH min and max values
- Recognize shorthand: "BP" = Big Pharma, common company abbreviations
- Therapeutic areas should be standardized: "oncology", "CNS", "immunology", "rare disease", "cardiovascular", "metabolic", etc.
- Phase experience: Use standard terms: "Preclinical", "Phase 1", "Phase 2", "Phase 3", "NDA/BLA"
- If information is not mentioned, use null for numbers, empty string for text, empty array for lists
- The "why_interesting" narrative should sound natural and highlight the most compelling aspects
- Return ONLY the JSON object, no additional text

Interview notes/transcript:
"""

def extract_candidate_info(transcript):
    """Use GPT-4 to extract structured candidate information from transcript"""
    try:
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a specialized AI assistant for executive recruiting in biotech/pharma. You extract structured data from interview notes with high accuracy."},
                {"role": "user", "content": EXTRACTION_PROMPT + transcript}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        extracted_data = json.loads(response.choices[0].message.content)
        return extracted_data

    except Exception as e:
        raise Exception(f"AI extraction failed: {str(e)}")

def generate_candidate_brief(candidate_data):
    """Generate formatted candidate brief for email/CRM"""
    name = candidate_data.get('name', 'Unknown')
    title = candidate_data.get('current_title', 'Unknown Title')
    company = candidate_data.get('current_company', 'Unknown Company')

    brief = f"{name} - {title} at {company}\n\n"

    # Key Qualifications
    brief += "KEY QUALIFICATIONS:\n"
    skills = candidate_data.get('technical_skills', [])
    if skills:
        for skill in skills[:8]:  # Top 8 skills
            brief += f"- {skill}\n"

    exp_total = candidate_data.get('years_experience_total')
    exp_therapeutic = candidate_data.get('years_experience_therapeutic')
    if exp_total:
        brief += f"- {exp_total} years total experience"
        if exp_therapeutic:
            brief += f" ({exp_therapeutic} years in relevant therapeutic area)"
        brief += "\n"

    therapeutic_areas = candidate_data.get('therapeutic_areas', [])
    if therapeutic_areas:
        brief += f"- Therapeutic expertise: {', '.join(therapeutic_areas)}\n"

    phase_exp = candidate_data.get('phase_experience', [])
    if phase_exp:
        brief += f"- Phase experience: {', '.join(phase_exp)}\n"

    # Compensation & Availability
    brief += "\nCOMPENSATION & AVAILABILITY:\n"

    curr_min = candidate_data.get('compensation_current_min')
    curr_max = candidate_data.get('compensation_current_max')
    targ_min = candidate_data.get('compensation_target_min')
    targ_max = candidate_data.get('compensation_target_max')

    if curr_min and curr_max:
        brief += f"- Current: ${curr_min:,}-${curr_max:,}K"
    elif curr_min:
        brief += f"- Current: ${curr_min:,}K"
    else:
        brief += "- Current: Not disclosed"

    if targ_min and targ_max:
        brief += f" | Target: ${targ_min:,}-${targ_max:,}K\n"
    elif targ_min:
        brief += f" | Target: ${targ_min:,}K\n"
    else:
        brief += " | Target: Not disclosed\n"

    notice_period = candidate_data.get('notice_period', 'Not specified')
    brief += f"- Available: {notice_period}\n"

    location = candidate_data.get('location', 'Not specified')
    relocation = "Y" if candidate_data.get('open_to_relocation') else "N"
    brief += f"- Location: {location} | Open to relocation: {relocation}\n"

    # Why Interesting
    why_interesting = candidate_data.get('why_interesting', '')
    if why_interesting:
        brief += f"\nWHY THIS CANDIDATE IS INTERESTING:\n{why_interesting}\n"

    # Red Flags
    red_flags = candidate_data.get('red_flags', '')
    if red_flags and red_flags.strip():
        brief += f"\nRED FLAGS / CONCERNS:\n{red_flags}\n"
    else:
        brief += "\nRED FLAGS / CONCERNS:\nNone identified\n"

    return brief
