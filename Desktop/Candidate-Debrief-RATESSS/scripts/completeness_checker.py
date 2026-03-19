#!/usr/bin/env python3
"""
Completeness Checker for RATESSS Debriefs

This script validates that all required RATESSS elements have been addressed
in a debrief conversation or written output. It checks for the presence of
key information, questions asked, and data captured.

Usage:
    python completeness_checker.py --file path/to/debrief_notes.txt
    python completeness_checker.py --client-email path/to/client_email.txt
    python completeness_checker.py --internal-notes path/to/internal_notes.txt
"""

import re
import argparse
from typing import Dict, List, Set
from dataclasses import dataclass


@dataclass
class RATESSElement:
    """Represents a RATESSS framework element with its requirements."""
    name: str
    letter: str
    required_topics: List[str]
    key_questions: List[str]
    warning_if_missing: str


class CompletenessChecker:
    """Validates completeness of RATESSS debrief."""
    
    def __init__(self):
        # Define RATESSS elements and their requirements
        self.elements = {
            'R': RATESSElement(
                name='Relationships',
                letter='R',
                required_topics=[
                    'impressions of role',
                    'impressions of company',
                    'impressions of individuals',
                    'favorite aspects',
                    'hiring manager',
                    'team'
                ],
                key_questions=[
                    'how was the position described',
                    'what did you think of',
                    'what are your impressions',
                    'what stood out'
                ],
                warning_if_missing='Missing impressions of individuals met - CRITICAL for client feedback'
            ),
            'A': RATESSElement(
                name='Alternatives',
                letter='A',
                required_topics=[
                    'red flags',
                    'concerns',
                    'other opportunities',
                    'other interviews',
                    'competing offers',
                    'other processes'
                ],
                key_questions=[
                    'red flags',
                    'concerns',
                    'what other opportunities',
                    'where are you in the process',
                    'any pending offers'
                ],
                warning_if_missing='Missing competitive landscape - CRITICAL for timeline management'
            ),
            'T': RATESSElement(
                name='Timeline',
                letter='T',
                required_topics=[
                    'timeline',
                    'availability',
                    'next steps',
                    'other interview timelines',
                    'when available',
                    'notice period'
                ],
                key_questions=[
                    'when do you expect to hear',
                    'when would you be available',
                    'what is your notice period',
                    'timeline'
                ],
                warning_if_missing='Missing timeline information - needed for scheduling'
            ),
            'E': RATESSElement(
                name='Expectations',
                letter='E',
                required_topics=[
                    'compensation',
                    'salary',
                    'bonus',
                    'equity',
                    'title',
                    'expectations',
                    'current compensation'
                ],
                key_questions=[
                    'compensation expectations',
                    'what are you making',
                    'what title',
                    'bonus structure',
                    'equity'
                ],
                warning_if_missing='Missing compensation expectations - CRITICAL for offer preparation'
            ),
            'S1': RATESSElement(
                name='Sign Off',
                letter='S',
                required_topics=[
                    'decision',
                    'spouse',
                    'family',
                    'who else',
                    'when could you start'
                ],
                key_questions=[
                    'who else is involved',
                    'when could you start',
                    'family',
                    'spouse',
                    'partner'
                ],
                warning_if_missing='Missing "when could you start" question - CRITICAL temperature test'
            ),
            'S2': RATESSElement(
                name='Sell',
                letter='S',
                required_topics=[
                    'excited',
                    'impressed',
                    'liked',
                    'what specifically',
                    'career goals',
                    'alignment'
                ],
                key_questions=[
                    'what specifically',
                    'what excited you',
                    'what impressed you',
                    'how does this align'
                ],
                warning_if_missing='Missing specific positives - needed for reinforcement'
            ),
            'S3': RATESSElement(
                name='Steps/Strategy',
                letter='S',
                required_topics=[
                    'interested in moving forward',
                    'next stage',
                    'second interview',
                    'how was it left',
                    'interest level'
                ],
                key_questions=[
                    'interested in moving',
                    'would you like to proceed',
                    'how was the interview left',
                    'what happens next'
                ],
                warning_if_missing='Missing explicit interest confirmation'
            )
        }
    
    def check_element(self, text: str, element: RATESSElement) -> Dict:
        """Check if a specific RATESSS element is addressed."""
        text_lower = text.lower()
        
        # Check for required topics
        topics_found = []
        topics_missing = []
        for topic in element.required_topics:
            if topic in text_lower:
                topics_found.append(topic)
            else:
                topics_missing.append(topic)
        
        # Check for key questions
        questions_found = []
        questions_missing = []
        for question in element.key_questions:
            # More lenient matching - any significant part of the question
            question_parts = question.split()
            if len(question_parts) > 2:
                # If we find most of the words, consider it asked
                matches = sum(1 for part in question_parts if part in text_lower)
                if matches >= len(question_parts) * 0.6:  # 60% of words present
                    questions_found.append(question)
                else:
                    questions_missing.append(question)
            else:
                if question in text_lower:
                    questions_found.append(question)
                else:
                    questions_missing.append(question)
        
        # Determine coverage level
        topic_coverage = len(topics_found) / len(element.required_topics) if element.required_topics else 0
        question_coverage = len(questions_found) / len(element.key_questions) if element.key_questions else 0
        overall_coverage = (topic_coverage + question_coverage) / 2
        
        # Determine status
        if overall_coverage >= 0.7:
            status = 'COMPLETE'
        elif overall_coverage >= 0.4:
            status = 'PARTIAL'
        else:
            status = 'MISSING'
        
        return {
            'element': element.name,
            'letter': element.letter,
            'status': status,
            'coverage': overall_coverage,
            'topics_found': topics_found,
            'topics_missing': topics_missing,
            'questions_found': questions_found,
            'questions_missing': questions_missing,
            'warning': element.warning_if_missing if status != 'COMPLETE' else None
        }
    
    def check_critical_requirements(self, text: str) -> Dict:
        """Check for critical specific requirements."""
        text_lower = text.lower()
        critical_checks = {}
        
        # 1. "When could you start" question (temperature test)
        start_patterns = [
            r'when (could|would) you (be able to |possibly )?start',
            r'start date',
            r'how soon (could|would) you',
            r'availability to start'
        ]
        has_start_question = any(re.search(pattern, text_lower) for pattern in start_patterns)
        critical_checks['temperature_test'] = {
            'present': has_start_question,
            'importance': 'CRITICAL',
            'description': '"When could you start?" question (temperature test)'
        }
        
        # 2. Impressions of specific individuals
        individual_patterns = [
            r'what did you think of \w+',
            r'impressions? of \w+',
            r'how did you find \w+',
            r'thoughts? (on|about) \w+'
        ]
        has_individual_impressions = any(re.search(pattern, text_lower) 
                                         for pattern in individual_patterns)
        critical_checks['individual_impressions'] = {
            'present': has_individual_impressions,
            'importance': 'CRITICAL',
            'description': 'Specific impressions of individuals met'
        }
        
        # 3. Compensation expectations (specific numbers)
        comp_patterns = [
            r'\$[\d,]+k?',  # Dollar amounts
            r'\d{3,}\s?k',  # e.g., "150k"
            r'compensation expectation',
            r'salary expectation',
            r'what are you (making|earning)'
        ]
        has_comp_discussion = any(re.search(pattern, text_lower) 
                                 for pattern in comp_patterns)
        critical_checks['compensation'] = {
            'present': has_comp_discussion,
            'importance': 'CRITICAL',
            'description': 'Compensation expectations with specific numbers'
        }
        
        # 4. Competing opportunities
        competing_patterns = [
            r'other (opportunities|interviews|offers|processes)',
            r'(where|what) else',
            r'competing',
            r'other firms?'
        ]
        has_competing_info = any(re.search(pattern, text_lower) 
                                for pattern in competing_patterns)
        critical_checks['competing_landscape'] = {
            'present': has_competing_info,
            'importance': 'HIGH',
            'description': 'Information about competing opportunities'
        }
        
        # 5. Explicit interest confirmation
        interest_patterns = [
            r'interested in (moving|proceeding|next)',
            r'would you like to',
            r'interest level',
            r'how interested',
            r'scale of \d'
        ]
        has_interest_confirmation = any(re.search(pattern, text_lower) 
                                       for pattern in interest_patterns)
        critical_checks['interest_confirmation'] = {
            'present': has_interest_confirmation,
            'importance': 'HIGH',
            'description': 'Explicit confirmation of interest in proceeding'
        }
        
        # 6. Decision influencers
        influencer_patterns = [
            r'(spouse|partner|wife|husband)',
            r'who else is involved',
            r'family',
            r'discuss (with|this)',
            r'mentors?'
        ]
        has_influencer_info = any(re.search(pattern, text_lower) 
                                 for pattern in influencer_patterns)
        critical_checks['decision_influencers'] = {
            'present': has_influencer_info,
            'importance': 'MEDIUM',
            'description': 'Decision influencers identified'
        }
        
        return critical_checks
    
    def analyze(self, text: str) -> Dict:
        """Perform complete RATESSS completeness analysis."""
        results = {
            'overall_status': None,
            'completion_percentage': 0,
            'elements': {},
            'critical_checks': {},
            'warnings': [],
            'recommendations': []
        }
        
        # Check each RATESSS element
        element_statuses = []
        for key, element in self.elements.items():
            element_result = self.check_element(text, element)
            results['elements'][key] = element_result
            element_statuses.append(element_result['status'])
            
            # Add warnings for incomplete critical elements
            if element_result['status'] != 'COMPLETE' and element_result['warning']:
                results['warnings'].append(element_result['warning'])
        
        # Check critical requirements
        results['critical_checks'] = self.check_critical_requirements(text)
        
        # Add warnings for missing critical requirements
        for check_name, check_result in results['critical_checks'].items():
            if not check_result['present'] and check_result['importance'] == 'CRITICAL':
                results['warnings'].append(
                    f"CRITICAL: Missing {check_result['description']}"
                )
        
        # Calculate overall completion
        complete_count = sum(1 for status in element_statuses if status == 'COMPLETE')
        partial_count = sum(1 for status in element_statuses if status == 'PARTIAL')
        results['completion_percentage'] = (
            (complete_count + (partial_count * 0.5)) / len(self.elements)
        ) * 100
        
        # Determine overall status
        if results['completion_percentage'] >= 85:
            results['overall_status'] = 'EXCELLENT'
        elif results['completion_percentage'] >= 70:
            results['overall_status'] = 'GOOD'
        elif results['completion_percentage'] >= 50:
            results['overall_status'] = 'ACCEPTABLE'
        else:
            results['overall_status'] = 'INCOMPLETE'
        
        # Generate recommendations
        for key, element_result in results['elements'].items():
            if element_result['status'] == 'PARTIAL':
                missing_topics = element_result['topics_missing'][:2]  # Top 2
                results['recommendations'].append(
                    f"Complete {element_result['element']} section by addressing: "
                    f"{', '.join(missing_topics)}"
                )
            elif element_result['status'] == 'MISSING':
                results['recommendations'].append(
                    f"URGENT: Address {element_result['element']} section completely"
                )
        
        return results
    
    def print_report(self, results: Dict):
        """Print formatted completeness report."""
        print("=" * 70)
        print("RATESSS COMPLETENESS REPORT")
        print("=" * 70)
        print()
        
        # Overall Status
        print(f"OVERALL STATUS: {results['overall_status']}")
        print(f"Completion: {results['completion_percentage']:.0f}%")
        print()
        
        # Element-by-Element Breakdown
        print("RATESSS ELEMENT BREAKDOWN:")
        print("-" * 70)
        
        for key in ['R', 'A', 'T', 'E', 'S1', 'S2', 'S3']:
            element_result = results['elements'][key]
            status = element_result['status']
            
            # Status symbol
            if status == 'COMPLETE':
                symbol = '✓'
            elif status == 'PARTIAL':
                symbol = '⚠'
            else:
                symbol = '✗'
            
            print(f"\n{symbol} {element_result['letter']} - {element_result['element']}: {status}")
            print(f"   Coverage: {element_result['coverage']*100:.0f}%")
            
            if element_result['topics_found']:
                print(f"   Topics Addressed: {', '.join(element_result['topics_found'][:3])}")
            
            if element_result['topics_missing']:
                print(f"   Missing Topics: {', '.join(element_result['topics_missing'][:3])}")
            
            if status != 'COMPLETE' and element_result['questions_missing']:
                print(f"   Key Questions Not Asked: {element_result['questions_missing'][0]}")
        
        print()
        
        # Critical Requirements Check
        print("\nCRITICAL REQUIREMENTS:")
        print("-" * 70)
        
        for check_name, check_result in results['critical_checks'].items():
            symbol = '✓' if check_result['present'] else '✗'
            importance = check_result['importance']
            description = check_result['description']
            
            print(f"{symbol} [{importance}] {description}")
        
        print()
        
        # Warnings
        if results['warnings']:
            print("WARNINGS:")
            print("-" * 70)
            for warning in results['warnings']:
                print(f"  ⚠ {warning}")
            print()
        else:
            print("✓ No critical warnings")
            print()
        
        # Recommendations
        if results['recommendations']:
            print("RECOMMENDATIONS:")
            print("-" * 70)
            for i, rec in enumerate(results['recommendations'], 1):
                print(f"  {i}. {rec}")
            print()
        else:
            print("✓ No additional recommendations - debrief is complete")
            print()
        
        # Final Assessment
        print("FINAL ASSESSMENT:")
        print("-" * 70)
        if results['overall_status'] == 'EXCELLENT':
            print("  This debrief meets RATESSS standards. All critical elements")
            print("  have been addressed. Ready to generate outputs.")
        elif results['overall_status'] == 'GOOD':
            print("  This debrief is mostly complete. Address remaining items")
            print("  before generating final outputs.")
        elif results['overall_status'] == 'ACCEPTABLE':
            print("  This debrief has gaps. Complete missing sections before")
            print("  proceeding with output generation.")
        else:
            print("  This debrief is incomplete. Significant additional work needed")
            print("  to meet RATESSS standards. Review framework and re-conduct.")
        
        print()
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description='Validate completeness of RATESSS debrief'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Path to debrief notes file'
    )
    parser.add_argument(
        '--client-email',
        type=str,
        help='Path to client feedback email'
    )
    parser.add_argument(
        '--internal-notes',
        type=str,
        help='Path to internal red flags notes'
    )
    parser.add_argument(
        '--text',
        type=str,
        help='Direct text input'
    )
    
    args = parser.parse_args()
    
    # Determine which file to analyze
    file_path = args.file or args.client_email or args.internal_notes
    
    # Get text input
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found")
            return
        except Exception as e:
            print(f"Error reading file: {e}")
            return
    elif args.text:
        text = args.text
    else:
        print("Error: Must provide a file path or --text argument")
        parser.print_help()
        return
    
    # Analyze
    checker = CompletenessChecker()
    results = checker.analyze(text)
    checker.print_report(results)


if __name__ == "__main__":
    main()
