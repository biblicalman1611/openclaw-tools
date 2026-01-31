from enum import Enum
from typing import List, Dict
import re

class CoreTheme(Enum):
    WARFARE = "Spiritual Warfare"
    IDENTITY = "Kingdom Identity"
    AUTHORITY = "Divine Authority"
    COVENANT = "Covenant Relationship"
    TRANSFORMATION = "Inner Transformation"
    MISSION = "Kingdom Mission"
    INHERITANCE = "Spiritual Inheritance"
    VICTORY = "Overcoming Victory"

class ThemeCategorizer:
    def __init__(self):
        self.theme_keywords = {
            CoreTheme.WARFARE: [
                'battle', 'fight', 'warfare', 'enemy', 'resist', 'stand',
                'armor', 'weapon', 'victory', 'overcome'
            ],
            CoreTheme.IDENTITY: [
                'son', 'daughter', 'chosen', 'royal', 'priesthood', 'holy',
                'called', 'elect', 'identity', 'belong'
            ],
            CoreTheme.AUTHORITY: [
                'authority', 'power', 'dominion', 'rule', 'throne', 'reign',
                'command', 'decree', 'declare', 'establish'
            ],
            CoreTheme.COVENANT: [
                'covenant', 'promise', 'faithful', 'blood', 'seal', 'oath',
                'agreement', 'bond', 'commitment', 'relationship'
            ],
            CoreTheme.TRANSFORMATION: [
                'transform', 'renew', 'change', 'conform', 'image', 'glory',
                'process', 'growth', 'mature', 'develop'
            ],
            CoreTheme.MISSION: [
                'purpose', 'calling', 'mission', 'send', 'go', 'commission',
                'assignment', 'task', 'mandate', 'ministry'
            ],
            CoreTheme.INHERITANCE: [
                'inherit', 'inheritance', 'portion', 'promise', 'receive',
                'blessing', 'birthright', 'possession', 'heritage'
            ],
            CoreTheme.VICTORY: [
                'victory', 'triumph', 'overcome', 'conquer', 'prevail',
                'win', 'success', 'achievement', 'breakthrough'
            ]
        }
        
    def analyze_content(self, text: str) -> Dict[CoreTheme, float]:
        """Analyze content and return theme strength scores"""
        text = text.lower()
        word_count = len(text.split())
        scores = {}
        
        for theme, keywords in self.theme_keywords.items():
            theme_count = sum(text.count(keyword) for keyword in keywords)
            # Calculate normalized score (0-1)
            scores[theme] = min(theme_count / (word_count * 0.01), 1.0)
            
        return scores
    
    def get_primary_themes(self, text: str, threshold: float = 0.3) -> List[CoreTheme]:
        """Get primary themes that exceed the threshold"""
        scores = self.analyze_content(text)
        return [theme for theme, score in scores.items() if score >= threshold]
    
    def suggest_theme_enhancements(self, text: str) -> List[str]:
        """Suggest ways to strengthen weak themes"""
        scores = self.analyze_content(text)
        suggestions = []
        
        for theme, score in scores.items():
            if score < 0.3:
                keywords = ', '.join(self.theme_keywords[theme][:3])
                suggestions.append(
                    f"Consider strengthening {theme.value} theme using keywords: {keywords}"
                )
        
        return suggestions
    
    def categorize_content(self, text: str) -> Dict[str, any]:
        """Complete content categorization"""
        scores = self.analyze_content(text)
        primary_themes = self.get_primary_themes(text)
        suggestions = self.suggest_theme_enhancements(text)
        
        return {
            'theme_scores': {theme.value: score for theme, score in scores.items()},
            'primary_themes': [theme.value for theme in primary_themes],
            'suggestions': suggestions
        }