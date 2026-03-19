#!/usr/bin/env python3
"""
Tone Validator for RATESSS Client Communications

This script analyzes written client feedback emails to ensure they meet
professional standards defined in the Communication Rules. It calculates
a Formality Score (target: 7-9/10) and checks for prohibited language.

Usage:
    python tone_validator.py --file path/to/email.txt
    python tone_validator.py --text "Email content here"
"""

import re
import argparse
from typing import Dict, List, Tuple
from collections import Counter


class ToneValidator:
    """Validates professional tone and formality of recruiting communications."""
    
    # Prohibited words and phrases (from Communication_Rules.md)
    FILLER_WORDS = [
        'um', 'uh', 'like', 'you know', 'sort of', 'kind of', 'i mean', 'basically'
    ]
    
    WEAK_QUALIFIERS = [
        'maybe', 'perhaps', 'i think', 'possibly', 'it seems', 'i guess'
    ]
    
    HEDGING_LANGUAGE = [
        'to be honest', 'frankly', 'to tell you the truth', "if i'm being honest"
    ]
    
    APOLOGETIC_LANGUAGE = [
        "i'm sorry to ask", 'this might be a stupid question', 
        'i hate to bother you', 'sorry for the confusion'
    ]
    
    RECRUITING_JARGON = [
        'opportunity', 'reach out', 'touch base', 'circle back', 
        'bandwidth', 'on your radar', 'move the needle', 'low-hanging fruit', 
        'synergy'
    ]
    
    PUSHY_LANGUAGE = [
        'amazing opportunity you can\'t miss', 'you\'d be crazy not to', 
        'everyone wants this job', 'this won\'t be available long'
    ]
    
    # Positive indicators for professional tone
    PROFESSIONAL_PHRASES = [
        'i recommend', 'based on', 'in my experience', 'my assessment', 
        'specifically', 'particularly', 'expressed strong interest'
    ]
    
    def __init__(self):
        self.violations = []
        self.warnings = []
        self.strengths = []
        
    def calculate_formality_score(self, text: str) -> float:
        """
        Calculate formality score on 1-10 scale.
        Target: 7-9 (professional business communication)
        
        Factors:
        - Average sentence length (longer = more formal)
        - Passive vs active voice usage
        - Vocabulary complexity
        - Paragraph structure
        - Professional phrase usage
        """
        text_lower = text.lower()
        
        # Initialize score at neutral
        score = 5.0
        
        # Factor 1: Sentence length (professional emails use varied but complete sentences)
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            # Optimal: 15-25 words per sentence
            if 15 <= avg_sentence_length <= 25:
                score += 1.0
            elif 10 <= avg_sentence_length < 15 or 25 < avg_sentence_length <= 30:
                score += 0.5
            elif avg_sentence_length < 8:  # Too short/choppy
                score -= 0.5
            elif avg_sentence_length > 35:  # Too long/complex
                score -= 0.5
        
        # Factor 2: Contractions (fewer = more formal)
        contractions = len(re.findall(r"\w+'\w+", text))
        total_words = len(text.split())
        if total_words > 0:
            contraction_ratio = contractions / total_words
            if contraction_ratio < 0.02:  # Less than 2% contractions
                score += 1.0
            elif contraction_ratio < 0.05:
                score += 0.5
            elif contraction_ratio > 0.1:  # More than 10%
                score -= 1.0
        
        # Factor 3: Professional phrases present
        professional_count = sum(1 for phrase in self.PROFESSIONAL_PHRASES 
                                if phrase in text_lower)
        if professional_count >= 3:
            score += 1.0
        elif professional_count >= 1:
            score += 0.5
        
        # Factor 4: Paragraph structure (multiple paragraphs indicate formal structure)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if len(paragraphs) >= 4:
            score += 0.5
        elif len(paragraphs) >= 2:
            score += 0.25
        elif len(paragraphs) == 1 and len(text.split()) > 100:  # Long single block
            score -= 0.5
        
        # Factor 5: Vocabulary complexity (longer words = more formal)
        words = text.split()
        if words:
            avg_word_length = sum(len(w.strip('.,!?;:')) for w in words) / len(words)
            if avg_word_length >= 5.5:  # Professional vocabulary
                score += 0.5
            elif avg_word_length >= 4.5:
                score += 0.25
            elif avg_word_length < 3.5:  # Too simple
                score -= 0.5
        
        # Factor 6: Deductions for violations
        violation_count = len(self.violations)
        score -= (violation_count * 0.5)
        
        # Clamp score between 1 and 10
        return max(1.0, min(10.0, score))
    
    def check_prohibited_language(self, text: str) -> List[Dict[str, str]]:
        """Check for prohibited words and phrases."""
        text_lower = text.lower()
        found_violations = []
        
        # Check each category
        categories = [
            ('Filler Word', self.FILLER_WORDS),
            ('Weak Qualifier', self.WEAK_QUALIFIERS),
            ('Hedging Language', self.HEDGING_LANGUAGE),
            ('Apologetic Language', self.APOLOGETIC_LANGUAGE),
            ('Recruiting Jargon', self.RECRUITING_JARGON),
            ('Pushy Language', self.PUSHY_LANGUAGE)
        ]
        
        for category, phrases in categories:
            for phrase in phrases:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(phrase) + r'\b'
                matches = re.finditer(pattern, text_lower)
                for match in matches:
                    # Find the actual text (with original case)
                    start, end = match.span()
                    original_text = text[start:end]
                    found_violations.append({
                        'category': category,
                        'phrase': original_text,
                        'position': start
                    })
        
        return found_violations
    
    def check_sentence_structure(self, text: str) -> List[str]:
        """Check for sentence structure issues."""
        issues = []
        
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        for i, sentence in enumerate(sentences):
            words = sentence.split()
            
            # Check for very short sentences (fragments)
            if len(words) < 4 and len(words) > 0:
                issues.append(f"Sentence {i+1} may be too short/fragmentary: '{sentence}'")
            
            # Check for very long sentences
            if len(words) > 40:
                issues.append(f"Sentence {i+1} is very long ({len(words)} words). Consider breaking it up.")
            
            # Check for multiple 'and' or 'but' (run-on indicators)
            and_count = sentence.lower().count(' and ')
            but_count = sentence.lower().count(' but ')
            if and_count + but_count > 3:
                issues.append(f"Sentence {i+1} may be a run-on (multiple 'and'/'but' connectors)")
        
        return issues
    
    def check_paragraph_structure(self, text: str) -> List[str]:
        """Check paragraph structure."""
        issues = []
        
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Check for bullet points in client email
        if any(line.strip().startswith(('•', '-', '*', '1.', '2.')) 
               for line in text.split('\n')):
            issues.append("Email contains bullet points. Client emails should use full paragraph format.")
        
        # Check paragraph count
        if len(paragraphs) < 3:
            issues.append(f"Only {len(paragraphs)} paragraph(s). Professional emails typically have 4-7 paragraphs.")
        elif len(paragraphs) > 8:
            issues.append(f"Email has {len(paragraphs)} paragraphs. Consider consolidating (target: 4-7).")
        
        # Check individual paragraphs
        for i, para in enumerate(paragraphs):
            sentences = [s.strip() for s in re.split(r'[.!?]+', para) if s.strip()]
            
            # Single sentence paragraphs (should be avoided)
            if len(sentences) == 1 and len(para.split()) > 20:
                issues.append(f"Paragraph {i+1} is a single long sentence. Break it up.")
            
            # Very long paragraphs
            if len(sentences) > 8:
                issues.append(f"Paragraph {i+1} has {len(sentences)} sentences. Consider breaking it up.")
        
        return issues
    
    def analyze(self, text: str) -> Dict:
        """Perform complete analysis of text."""
        # Reset state
        self.violations = []
        self.warnings = []
        self.strengths = []
        
        # Run checks
        prohibited = self.check_prohibited_language(text)
        sentence_issues = self.check_sentence_structure(text)
        paragraph_issues = self.check_paragraph_structure(text)
        
        # Calculate formality score
        formality_score = self.calculate_formality_score(text)
        
        # Categorize prohibited language
        self.violations = prohibited
        self.warnings = sentence_issues + paragraph_issues
        
        # Identify strengths
        text_lower = text.lower()
        for phrase in self.PROFESSIONAL_PHRASES:
            if phrase in text_lower:
                self.strengths.append(f"Uses professional phrase: '{phrase}'")
        
        # Word count
        word_count = len(text.split())
        
        # Overall assessment
        if formality_score >= 7 and formality_score <= 9:
            assessment = "EXCELLENT - Meets professional standards"
        elif formality_score >= 6 and formality_score <= 10:
            assessment = "GOOD - Acceptable with minor improvements"
        elif formality_score >= 5:
            assessment = "FAIR - Needs improvement"
        else:
            assessment = "POOR - Significant revision needed"
        
        return {
            'formality_score': formality_score,
            'target_range': '7-9',
            'assessment': assessment,
            'word_count': word_count,
            'violations': self.violations,
            'warnings': self.warnings,
            'strengths': self.strengths
        }
    
    def print_report(self, results: Dict):
        """Print formatted analysis report."""
        print("=" * 70)
        print("TONE VALIDATION REPORT")
        print("=" * 70)
        print()
        
        # Formality Score
        score = results['formality_score']
        print(f"FORMALITY SCORE: {score:.1f}/10")
        print(f"Target Range: {results['target_range']}")
        print(f"Assessment: {results['assessment']}")
        print()
        
        # Word Count
        print(f"Word Count: {results['word_count']}")
        print(f"Target Range: 300-500 words for client emails")
        print()
        
        # Violations
        if results['violations']:
            print("VIOLATIONS FOUND:")
            print("-" * 70)
            violation_counts = Counter(v['category'] for v in results['violations'])
            for category, count in violation_counts.items():
                print(f"\n{category} ({count} instance(s)):")
                violations_in_category = [v for v in results['violations'] 
                                         if v['category'] == category]
                for v in violations_in_category:
                    print(f"  - '{v['phrase']}'")
            print()
        else:
            print("✓ No prohibited language violations found")
            print()
        
        # Warnings
        if results['warnings']:
            print("WARNINGS:")
            print("-" * 70)
            for warning in results['warnings']:
                print(f"  ⚠ {warning}")
            print()
        else:
            print("✓ No structural warnings")
            print()
        
        # Strengths
        if results['strengths']:
            print("STRENGTHS:")
            print("-" * 70)
            for strength in results['strengths']:
                print(f"  ✓ {strength}")
            print()
        
        # Recommendations
        print("RECOMMENDATIONS:")
        print("-" * 70)
        if score < 7:
            print("  • Increase formality by using complete sentences and professional vocabulary")
            print("  • Remove any casual language or contractions")
            print("  • Structure content in clear paragraphs (4-7 paragraphs ideal)")
        elif score > 9:
            print("  • Slightly reduce formality to avoid sounding stiff")
            print("  • Ensure content remains warm and engaging")
        else:
            print("  • Formality level is appropriate - maintain current tone")
        
        if results['word_count'] < 300:
            print("  • Consider adding more detail (target: 300-500 words)")
        elif results['word_count'] > 600:
            print("  • Consider condensing (target: 300-500 words)")
        
        if results['violations']:
            print("  • Remove all prohibited language identified above")
        
        print()
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description='Validate tone and formality of recruiting communications'
    )
    parser.add_argument(
        '--file', 
        type=str, 
        help='Path to text file containing email'
    )
    parser.add_argument(
        '--text', 
        type=str, 
        help='Direct text input (alternative to --file)'
    )
    
    args = parser.parse_args()
    
    # Get text input
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found")
            return
        except Exception as e:
            print(f"Error reading file: {e}")
            return
    elif args.text:
        text = args.text
    else:
        print("Error: Must provide either --file or --text argument")
        parser.print_help()
        return
    
    # Analyze
    validator = ToneValidator()
    results = validator.analyze(text)
    validator.print_report(results)


if __name__ == "__main__":
    main()
