"""
assertions.py
Binary assertion functions for rapid-source skill evaluation.

Each function takes:
  output   (str): full LLM output text
  metadata (dict): test case metadata

Returns True (pass) or False (fail).

Design notes:
- LLM output formatting is not guaranteed to be consistent.
- All extractors use multiple regex patterns with fallbacks.
- Assertions lean toward generous interpretation to avoid false failures
  on cosmetic formatting variation; they're strict only on substance.
"""

import re
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Shared extraction helpers
# ---------------------------------------------------------------------------

def _extract_boolean_strings(output: str) -> List[str]:
    """
    Extract Boolean search string content from the output.
    Tries multiple patterns in order of specificity:
      1. Fenced code blocks (``` ... ```)
      2. Lines that look like Boolean strings (contain OR/AND/NOT with
         parentheses, typical of LinkedIn Recruiter syntax)
      3. Paragraphs following common Boolean section labels
    Returns a list of string blobs, one per Boolean string found.
    """
    results = []

    # Pattern 1: fenced code blocks (triple backtick)
    fenced = re.findall(r'```[^\n]*\n(.*?)```', output, re.DOTALL)
    results.extend([b.strip() for b in fenced if b.strip()])

    if results:
        return results

    # Pattern 2: inline code-like blocks with leading/trailing backtick lines
    # Some LLMs output boolean strings without fences but with quote-like wrapping
    quoted = re.findall(r'(?:^|\n)([("].+? OR .+?NOT .+?)(?:\n\n|\Z)', output, re.DOTALL | re.MULTILINE)
    results.extend([b.strip() for b in quoted if b.strip()])

    if results:
        return results

    # Pattern 3: look for the BOOLEAN section and extract multi-line query blocks
    # by searching for lines that contain several OR operators
    boolean_section_match = re.search(
        r'(?:BOOLEAN|SEARCH STRING|BOOLEAN STRING)S?\s*\n+(.*?)(?:\n#+\s|\Z)',
        output,
        re.DOTALL | re.IGNORECASE
    )
    if boolean_section_match:
        section = boolean_section_match.group(1)
        # Extract paragraphs with OR operators (typical of a Boolean string)
        paragraphs = re.split(r'\n{2,}', section)
        for para in paragraphs:
            if para.count(' OR ') >= 2:
                results.append(para.strip())

    return results


def _extract_inmail_bodies(output: str) -> List[str]:
    """
    Extract InMail body text (between Subject line and signature).
    Returns a list of body strings, one per InMail found.
    Falls back to extracting all content after the INMAIL section header
    if the structural pattern doesn't match.
    """
    bodies = []

    # Pattern 1: Subject: ... body ... Bryan Blair
    # Handles both Template A/B and unlabeled InMails
    pattern = re.compile(
        r'Subject\s*:\s*[^\n]+\n+'         # Subject line
        r'(.*?)'                             # Body (captured)
        r'(?:Bryan Blair|GQR Global|'        # Signature start variants
        r'---+\s*$|\Z)',                     # or horizontal rule or end
        re.DOTALL | re.IGNORECASE
    )
    matches = pattern.findall(output)
    if matches:
        bodies = [m.strip() for m in matches if m.strip()]
        # Filter out bodies that are clearly too short to be real InMails
        bodies = [b for b in bodies if len(b.split()) >= 20]

    if bodies:
        return bodies

    # Pattern 2: Look for numbered or labeled InMail blocks
    labeled = re.split(
        r'(?:InMail\s+(?:Template\s+)?[AB12]|Template\s+[AB])\s*\n',
        output,
        flags=re.IGNORECASE
    )
    if len(labeled) > 1:
        for block in labeled[1:]:
            # Find Subject: within block, grab body after it
            subj_match = re.search(r'Subject\s*:[^\n]+\n+(.*?)(?:Bryan Blair|\Z)', block, re.DOTALL | re.IGNORECASE)
            if subj_match:
                body = subj_match.group(1).strip()
                if len(body.split()) >= 20:
                    bodies.append(body)

    if bodies:
        return bodies

    # Pattern 3: Take everything after INMAIL section header as a fallback blob
    inmail_start = re.search(r'(?:##?\s+)?(?:\d\.\s+)?INMAIL', output, re.IGNORECASE)
    if inmail_start:
        inmail_blob = output[inmail_start.start():]
        bodies = [inmail_blob]

    return bodies


def _get_boolean_section(output: str) -> str:
    """
    Return the portion of output that contains Boolean strings.
    Stops at INMAIL section to avoid false positives from InMail text.
    """
    upper = output.upper()
    inmail_pos = upper.find('INMAIL')
    if inmail_pos == -1:
        return output
    return output[:inmail_pos]


def _get_inmail_section(output: str) -> str:
    """
    Return the portion of output starting from the first InMail.
    """
    upper = output.upper()
    inmail_pos = upper.find('INMAIL')
    if inmail_pos == -1:
        # Try to find Subject: as fallback
        subj_pos = output.lower().find('subject:')
        if subj_pos != -1:
            return output[subj_pos:]
        return ''
    return output[inmail_pos:]


# ---------------------------------------------------------------------------
# Assertion functions
# ---------------------------------------------------------------------------

def assert_boolean_depth(output: str, metadata: Dict) -> bool:
    """
    Each Boolean string has 3+ OR groups (clusters).
    A cluster is defined as a group of terms separated by OR operators.
    We require at least 3 such groupings per string.
    Also requires at least 3 Boolean strings in the output.
    """
    booleans = _extract_boolean_strings(output)

    if len(booleans) < 3:
        # Soft check: maybe the output has 3 angle labels but not all are
        # in code blocks. Count angle/label lines as a proxy.
        angle_labels = re.findall(
            r'(?:CORE MATCH|ADJACENT|SPONSOR.SIDE|BIG PHARMA|THERAPEUTIC|SYSTEM|TOOL)',
            output,
            re.IGNORECASE
        )
        if len(angle_labels) < 3:
            return False
        # If we can find the labels but not the strings, be lenient - it's
        # a formatting issue, not a substance issue. Check what we have.
        if not booleans:
            return False

    # For each extracted Boolean string, check it has at least 3 OR groups
    def has_three_clusters(b: str) -> bool:
        # Count OR occurrences (as whole words, case-insensitive)
        or_count = len(re.findall(r'\bOR\b', b, re.IGNORECASE))
        return or_count >= 3

    # If we got fewer than 3 strings but all pass the depth check,
    # still require at least 3 strings
    passing = [b for b in booleans if has_three_clusters(b)]
    return len(booleans) >= 3 and len(passing) >= 3


def assert_not_block(output: str, metadata: Dict) -> bool:
    """
    Every Boolean string includes a NOT block for seniority exclusion.
    Accepts NOT(...), NOT "...", or NOT followed by seniority terms.
    """
    booleans = _extract_boolean_strings(output)

    if not booleans:
        # Fall back: check for NOT in the Boolean section of raw output
        bool_section = _get_boolean_section(output)
        not_matches = re.findall(r'\bNOT\b', bool_section, re.IGNORECASE)
        return len(not_matches) >= 3  # One per expected Boolean string

    def has_not_block(b: str) -> bool:
        # Look for NOT(...) pattern
        if re.search(r'\bNOT\s*\(', b, re.IGNORECASE):
            return True
        # Look for NOT followed by a quoted term
        if re.search(r'\bNOT\s+"', b, re.IGNORECASE):
            return True
        # Look for NOT followed by seniority-related terms
        seniority_terms = ['director', 'vp', 'vice president', 'svp', 'chief',
                           'coordinator', 'associate', 'intern', 'head of', 'coo', 'cmo']
        for term in seniority_terms:
            if re.search(r'\bNOT\b.*' + re.escape(term), b, re.IGNORECASE):
                return True
        return False

    return all(has_not_block(b) for b in booleans)


# Company names that should NOT appear in InMail sections
# These come from the test JDs. The assertion checks that real company names
# from the JD don't leak into the InMail (which should use anonymous descriptions).
_COMPANY_NAME_PATTERNS = [
    # From test JDs
    r'\bStructure Therapeutics\b',
    r'\bIdeaya\b',
    r'\bKaryopharm\b',
    r'\bApogee Therapeutics\b',
    r'\bInsmed\b',
    r'\bRegeneron\b',
    r'\bGenentech\b',
    r'\bGilead\b',
    r'\bAbbVie\b',
    r'\bAmgen\b',
    r'\bPfizer\b',
    r'\bNovartis\b',
    r'\bRoche\b',
    r'\bBiogen\b',
    r'\bVertex Pharmaceuticals\b',
    r'\bSarepta\b',
    r'\bbluebird bio\b',
    r'\bModerna\b',
    r'\bBioMarin\b',
    r'\bAlexion\b',
    # Generic but telling phrases
    r'\bthe client\b',  # "the client" is also a leak pattern
]

# Pre-compiled patterns for performance
_COMPILED_COMPANY_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in _COMPANY_NAME_PATTERNS
]


def assert_client_anonymized(output: str, metadata: Dict) -> bool:
    """
    InMails never name the client company.
    Checks the InMail + follow-up section for company name leakage.
    """
    inmail_section = _get_inmail_section(output)
    if not inmail_section:
        # No identifiable InMail section — can't verify, so fail
        return False

    for pattern in _COMPILED_COMPANY_PATTERNS:
        if pattern.search(inmail_section):
            return False

    return True


def assert_word_count(output: str, metadata: Dict) -> bool:
    """
    Each InMail body is 120 words or fewer (130 with a 10-word grace for
    formatting artifacts like the signature being partially included).
    """
    bodies = _extract_inmail_bodies(output)

    if not bodies:
        return False

    WORD_LIMIT = 130  # 120 + 10-word grace

    for body in bodies:
        # Remove the signature line if it got captured
        cleaned = re.sub(
            r'Bryan Blair.*?(?:GQR Global Markets|$)',
            '',
            body,
            flags=re.DOTALL | re.IGNORECASE
        ).strip()
        word_count = len(cleaned.split())
        if word_count > WORD_LIMIT:
            return False

    return True


_BANNED_PHRASES = [
    'exciting opportunity',
    'hope this finds you well',
    'i came across your profile',
    'proven track record',
    'thrilling',
    'amazing',
    'resume',
    'phase 1+',
    'just following up',
    'bumping this',
    'hope you are well',
    'i hope this email',
    'i wanted to reach out',
    'i am reaching out',
    'touch base',
    'circling back',
]

# Em dash and en dash Unicode characters
_EM_DASH = '\u2014'
_EN_DASH = '\u2013'


def assert_no_banned_phrases(output: str, metadata: Dict) -> bool:
    """
    Zero banned phrases, em dashes, en dashes, exclamation points in InMails,
    or 'resume' anywhere in the output.
    """
    lower_output = output.lower()

    # Check banned phrases against full output (some apply everywhere)
    for phrase in _BANNED_PHRASES:
        if phrase in lower_output:
            return False

    # Check em/en dashes anywhere in output
    if _EM_DASH in output or _EN_DASH in output:
        return False

    # Check exclamation points only in InMail/follow-up section
    inmail_section = _get_inmail_section(output)
    if inmail_section and '!' in inmail_section:
        return False

    return True


_WEAK_ENDING_WORDS = {
    'it', 'this', 'that', 'them', 'here', 'there', 'well', 'me', 'us',
    'so', 'too', 'now', 'then', 'out', 'up', 'in', 'on', 'at', 'to',
    'do', 'be', 'is', 'are', 'was', 'were', 'week', 'you', 'your',
}


def assert_impact_endings(output: str, metadata: Dict) -> bool:
    """
    Hook and CTA sentences end on high-weight words.
    We check the first sentence (hook) and last non-signature sentence (CTA)
    of each InMail body.
    """
    bodies = _extract_inmail_bodies(output)

    if not bodies:
        return False

    for body in bodies:
        # Remove signature
        cleaned = re.sub(
            r'Bryan Blair.*',
            '',
            body,
            flags=re.DOTALL | re.IGNORECASE
        ).strip()

        if not cleaned:
            continue

        # Split into sentences
        sentences = re.findall(r'[A-Z][^.!?]*[.!?]', cleaned)
        if not sentences:
            # Try splitting on periods only
            sentences = [s.strip() for s in cleaned.split('.') if s.strip()]

        if not sentences:
            continue

        # Check first sentence (hook) and last sentence (CTA)
        check_sentences = []
        check_sentences.append(sentences[0])
        if len(sentences) > 1:
            check_sentences.append(sentences[-1])

        for sentence in check_sentences:
            words = sentence.strip().rstrip('.!?').split()
            if not words:
                continue
            last_word = words[-1].lower().strip(",.;:'\"")
            if last_word in _WEAK_ENDING_WORDS:
                return False

    return True


def assert_onsite_disclosure(output: str, metadata: Dict) -> bool:
    """
    If the role requires 3+ days onsite per week, the InMail must mention
    location/onsite requirement.
    """
    onsite_days = metadata.get('onsite_days', 0)

    # Auto-pass for fully remote or light hybrid roles
    if onsite_days < 3:
        return True

    inmail_section = _get_inmail_section(output)
    if not inmail_section:
        return False

    location_terms = [
        'onsite', 'on-site', 'on site',
        'hybrid', 'days per week', 'days/week', 'd/w',
        'days on-site', 'days on site', 'in-office', 'in office',
        'based in', 'office-based', 'reporting to the',
        # Specific city patterns (onsite roles have cities in the JDs)
        'san francisco', 'south san francisco', 'newton', 'cambridge',
        'tarrytown', 'north chicago', 'bridgewater', 'foster city',
        'boston', 'somerville', 'waltham', 'san diego',
        # Day-count patterns
        'four days', '4 days', 'three days', '3 days', 'five days', '5 days',
        'full-time onsite', 'fully onsite',
    ]

    inmail_lower = inmail_section.lower()
    return any(term in inmail_lower for term in location_terms)


def assert_cro_logic(output: str, metadata: Dict) -> bool:
    """
    CRO is excluded (via NOT block) for clinical_ops roles.
    CRO is NOT excluded for drug_safety_pv, biometrics, and cdm roles.
    Other functions: auto-pass.
    """
    function = metadata.get('function', '')

    if function not in ('clinical_ops', 'drug_safety_pv', 'biometrics', 'cdm'):
        return True

    # Only analyze the Boolean strings section (before InMail starts)
    bool_section = _get_boolean_section(output)

    # Detect CRO exclusion: any NOT block that contains CRO or known CRO names
    cro_exclusion_patterns = [
        r'NOT\s*\([^)]*\bCRO\b[^)]*\)',          # NOT ("CRO" ...) or NOT (CRO)
        r'NOT\s+"CRO"',                             # NOT "CRO"
        r'NOT\s+CRO\b',                             # NOT CRO (bare)
        r'NOT\s*\([^)]*(?:IQVIA|PAREXEL|COVANCE|ICON|PPD|LABCORP DRUG)[^)]*\)',  # CRO name in NOT block
        r'NOT\s*\([^)]*"CONTRACT RESEARCH ORGAN[^)]*\)',
    ]

    cro_excluded = False
    for pattern in cro_exclusion_patterns:
        if re.search(pattern, bool_section, re.IGNORECASE):
            cro_excluded = True
            break

    # Also check for CRO appearing inside any NOT(...) block
    not_blocks = re.findall(r'NOT\s*\([^)]+\)', bool_section, re.IGNORECASE)
    if any(re.search(r'\bCRO\b', block, re.IGNORECASE) for block in not_blocks):
        cro_excluded = True

    if function == 'clinical_ops':
        return cro_excluded  # CRO MUST be excluded
    else:
        return not cro_excluded  # CRO must NOT be excluded


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

ASSERTIONS = [
    assert_boolean_depth,
    assert_not_block,
    assert_client_anonymized,
    assert_word_count,
    assert_no_banned_phrases,
    assert_impact_endings,
    assert_onsite_disclosure,
    assert_cro_logic,
]

ASSERTION_NAMES = [
    'boolean_depth',
    'not_block',
    'client_anonymized',
    'word_count',
    'no_banned_phrases',
    'impact_endings',
    'onsite_disclosure',
    'cro_logic',
]


def run_all_assertions(output: str, metadata: Dict) -> Dict[str, bool]:
    """
    Run all assertions and return a dict of {assertion_name: pass/fail}.
    """
    results = {}
    for fn, name in zip(ASSERTIONS, ASSERTION_NAMES):
        try:
            results[name] = fn(output, metadata)
        except Exception as e:
            # Assertion errors count as failures; log the error text
            results[name] = False
            results[f'{name}_error'] = str(e)
    return results


def all_pass(results: Dict[str, bool]) -> bool:
    """Return True only if every assertion passed (no error keys)."""
    return all(v for k, v in results.items() if not k.endswith('_error'))
