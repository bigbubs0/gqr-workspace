"""
Brand Voice Analyzer
Analyzes the formality, tone, and professionalism of client feedback emails.

This script validates that generated client communication adheres to the 
professional standards required by the RATESSS methodology.
"""

import re
from typing import Dict, List, Tuple


class BrandVoiceAnalyzer:
    """Analyzes text for formality, tone, and adherence to brand voice standards."""
    
    # Prohibited words and phrases (jargon, filler, casual language)
    PROHIBITED_TERMS = [
        'uh', 'um', 'you know', 'like', 'basically', 'actually', 
        'obviously', 'frankly', 'to be honest', 'awesome', 'cool', 
        'sweet', 'no worries', 'sounds good'
    ]
    
    # Weak qualifiers that undermine authority
    WEAK_QUALIFIERS = [
        'i think maybe', 'perhaps possibly', 'it might be', 
        'hopefully', 'i guess', 'sort of', 'kind of'
    ]
    
    # Professional vocabulary (positive indicators)
    PROFESSIONAL_TERMS = [
        'impressed', 'valuable', 'strategic', 'thoughtful', 'comprehensive',
        'alignment', 'trajectory', 'opportunities', 'capability', 'expertise'
    ]
    
    def __init__(self, text: str):
        """
        Initialize analyzer with text to analyze.
        
        Args:
            text: The email or document text to analyze
        """
        self.text = text
        self.text_lower = text.lower()
        self.word_count = len(text.split())
        self.sentence_count = len(re.split(r'[.!?]+', text))
        
    def analyze(self) -> Dict:
        """
        Perform complete analysis of the text.
        
        Returns:
            Dictionary containing all analysis results
        """
        return {
            'formality_score': self.calculate_formality_score(),
            'prohibited_terms_found': self.find_prohibited_terms(),
            'weak_qualifiers_found': self.find_weak_qualifiers(),
            'professional_vocabulary_count': self.count_professional_vocabulary(),
            'bullet_points_used': self.check_bullet_points(),
            'average_sentence_length': self.calculate_avg_sentence_length(),
            'passive_voice_percentage': self.estimate_passive_voice(),
            'overall_assessment': None  # Will be calculated
        }
        
    def calculate_formality_score(self) -> int:
        """
        Calculate formality score (0-100).
        
        Higher scores indicate more formal, professional communication.
        
        Returns:
            Integer score between 0 and 100
        """
        score = 70  # Start at baseline professional level
        
        # Deduct for prohibited terms
        prohibited_count = len(self.find_prohibited_terms())
        score -= (prohibited_count * 5)
        
        # Deduct for weak qualifiers
        weak_count = len(self.find_weak_qualifiers())
        score -= (weak_count * 3)
        
        # Add for professional vocabulary
        prof_count = self.count_professional_vocabulary()
        score += min(prof_count * 2, 20)  # Cap at +20
        
        # Deduct for bullet points (should use paragraphs)
        if self.check_bullet_points():
            score -= 10
            
        # Deduct for excessive passive voice
        passive_pct = self.estimate_passive_voice()
        if passive_pct > 30:
            score -= 10
            
        # Adjust for sentence length (too short = casual, too long = stuffy)
        avg_length = self.calculate_avg_sentence_length()
        if avg_length < 10:
            score -= 5  # Too casual
        elif avg_length > 30:
            score -= 5  # Too complex
            
        # Ensure score stays within 0-100
        return max(0, min(100, score))
        
    def find_prohibited_terms(self) -> List[str]:
        """
        Find all prohibited terms (jargon, filler words) in text.
        
        Returns:
            List of prohibited terms found
        """
        found = []
        for term in self.PROHIBITED_TERMS:
            if term in self.text_lower:
                # Get context around the term
                pattern = r'.{0,30}' + re.escape(term) + r'.{0,30}'
                matches = re.finditer(pattern, self.text_lower, re.IGNORECASE)
                for match in matches:
                    found.append(f"'{term}' found in: ...{match.group()}...")
        return found
        
    def find_weak_qualifiers(self) -> List[str]:
        """
        Find weak qualifiers that undermine authority.
        
        Returns:
            List of weak qualifiers found
        """
        found = []
        for qualifier in self.WEAK_QUALIFIERS:
            if qualifier in self.text_lower:
                pattern = r'.{0,30}' + re.escape(qualifier) + r'.{0,30}'
                matches = re.finditer(pattern, self.text_lower, re.IGNORECASE)
                for match in matches:
                    found.append(f"'{qualifier}' found in: ...{match.group()}...")
        return found
        
    def count_professional_vocabulary(self) -> int:
        """
        Count usage of professional vocabulary terms.
        
        Returns:
            Count of professional terms used
        """
        count = 0
        for term in self.PROFESSIONAL_TERMS:
            count += self.text_lower.count(term)
        return count
        
    def check_bullet_points(self) -> bool:
        """
        Check if text uses bullet points (not recommended for client emails).
        
        Returns:
            True if bullet points found, False otherwise
        """
        # Check for common bullet point markers
        bullet_patterns = [
            r'^\s*[-•*]\s',  # Dash, bullet, asterisk at line start
            r'^\s*\d+\.\s',  # Numbered list
            r'^\s*[a-z]\.\s',  # Lettered list
        ]
        
        for pattern in bullet_patterns:
            if re.search(pattern, self.text, re.MULTILINE):
                return True
        return False
        
    def calculate_avg_sentence_length(self) -> float:
        """
        Calculate average sentence length in words.
        
        Returns:
            Average number of words per sentence
        """
        if self.sentence_count == 0:
            return 0
        return self.word_count / self.sentence_count
        
    def estimate_passive_voice(self) -> float:
        """
        Estimate percentage of passive voice usage.
        
        This is a heuristic estimate based on common passive constructions.
        
        Returns:
            Estimated percentage of passive voice (0-100)
        """
        # Common passive voice patterns
        passive_patterns = [
            r'\b(is|are|was|were|been|be)\s+\w+ed\b',
            r'\b(is|are|was|were|been|be)\s+being\s+\w+ed\b',
        ]
        
        passive_count = 0
        for pattern in passive_patterns:
            passive_count += len(re.findall(pattern, self.text_lower))
            
        if self.sentence_count == 0:
            return 0
            
        return min((passive_count / self.sentence_count) * 100, 100)
        
    def get_assessment_report(self) -> str:
        """
        Generate a comprehensive assessment report.
        
        Returns:
            Formatted string with complete analysis
        """
        results = self.analyze()
        
        # Determine overall assessment
        score = results['formality_score']
        if score >= 85:
            overall = "EXCELLENT - Professional and polished"
        elif score >= 70:
            overall = "GOOD - Meets professional standards"
        elif score >= 50:
            overall = "ACCEPTABLE - Minor improvements needed"
        else:
            overall = "NEEDS REVISION - Below professional standards"
            
        results['overall_assessment'] = overall
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           BRAND VOICE ANALYSIS REPORT                        ║
╚══════════════════════════════════════════════════════════════╝

FORMALITY SCORE: {score}/100

OVERALL ASSESSMENT: {overall}

═══════════════════════════════════════════════════════════════

DETAILED FINDINGS:

1. PROHIBITED TERMS ({len(results['prohibited_terms_found'])} found)
   {'   ❌ ' + '   ❌ '.join(results['prohibited_terms_found']) if results['prohibited_terms_found'] else '   ✓ No prohibited terms found'}

2. WEAK QUALIFIERS ({len(results['weak_qualifiers_found'])} found)
   {'   ❌ ' + '   ❌ '.join(results['weak_qualifiers_found']) if results['weak_qualifiers_found'] else '   ✓ No weak qualifiers found'}

3. PROFESSIONAL VOCABULARY
   ✓ Professional terms used: {results['professional_vocabulary_count']}
   {('   ⚠ Consider using more professional vocabulary' if results['professional_vocabulary_count'] < 5 else '   ✓ Good use of professional language')}

4. FORMAT
   {'   ❌ Bullet points detected - use paragraph form instead' if results['bullet_points_used'] else '   ✓ Proper paragraph format'}

5. SENTENCE STRUCTURE
   Average sentence length: {results['average_sentence_length']:.1f} words
   {self._assess_sentence_length(results['average_sentence_length'])}

6. VOICE
   Passive voice: ~{results['passive_voice_percentage']:.1f}%
   {('   ⚠ Consider using more active voice' if results['passive_voice_percentage'] > 30 else '   ✓ Good balance of active voice')}

═══════════════════════════════════════════════════════════════

RECOMMENDATIONS:
{self._generate_recommendations(results)}

═══════════════════════════════════════════════════════════════
"""
        return report
        
    def _assess_sentence_length(self, avg_length: float) -> str:
        """Assess whether sentence length is appropriate."""
        if avg_length < 10:
            return "   ⚠ Sentences too short - may seem choppy or casual"
        elif avg_length > 30:
            return "   ⚠ Sentences too long - may be hard to follow"
        else:
            return "   ✓ Good sentence length for readability"
            
    def _generate_recommendations(self, results: Dict) -> str:
        """Generate specific recommendations based on results."""
        recommendations = []
        
        if results['prohibited_terms_found']:
            recommendations.append("• Remove prohibited terms and filler words")
            
        if results['weak_qualifiers_found']:
            recommendations.append("• Eliminate weak qualifiers that undermine authority")
            
        if results['professional_vocabulary_count'] < 5:
            recommendations.append("• Incorporate more professional vocabulary")
            
        if results['bullet_points_used']:
            recommendations.append("• Convert bullet points to paragraph format")
            
        if results['passive_voice_percentage'] > 30:
            recommendations.append("• Reduce passive voice usage")
            
        if results['formality_score'] < 70:
            recommendations.append("• Overall tone needs to be more professional")
            
        if not recommendations:
            recommendations.append("• No major revisions needed - ready to send!")
            
        return "\\n".join(recommendations)


def analyze_email(email_text: str) -> None:
    """
    Analyze an email and print the assessment report.
    
    Args:
        email_text: The complete email text to analyze
    """
    analyzer = BrandVoiceAnalyzer(email_text)
    print(analyzer.get_assessment_report())


def analyze_file(filepath: str) -> None:
    """
    Analyze a text file and print the assessment report.
    
    Args:
        filepath: Path to the file to analyze
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    analyze_email(text)


if __name__ == "__main__":
    # Example usage
    sample_email = """
    Michael,

    I spoke with Sarah Johnson this afternoon to debrief her interview with 
    Etrel Corporation, and I wanted to share her feedback with you while it's fresh.

    Overall, Sarah was genuinely impressed with the conversation and the organization. 
    She found the discussion highly engaging and sees strong alignment between the role 
    and her background in scaling operations for growth-stage companies.

    The role was described as VP of Operations with responsibility for building 
    infrastructure to support your expansion from $50M to $200M in revenue. Sarah was 
    particularly excited about the strategic nature of the position and the opportunity 
    to build systems from the ground up rather than inherit legacy processes.

    Sarah is very interested in moving forward and indicated that Etrel is her top 
    priority among the opportunities she's considering. She's available for next steps 
    and could meet with your board member next week if you'd like to move forward quickly.

    Please let me know your thoughts on bringing her back for the next stage.

    Best regards,
    Bryan
    """
    
    print("Analyzing sample client feedback email...")
    print("=" * 65)
    analyze_email(sample_email)
