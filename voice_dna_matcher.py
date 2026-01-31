import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
nltk.download('punkt')

class VoiceDNAMatcher:
    def __init__(self):
        self.target_avg_words = 8.5
        self.target_short_ratio = 0.62
        self.combat_metaphors = [
            'battle', 'war', 'fight', 'sword', 'shield', 'armor', 'warrior',
            'victory', 'conquer', 'defend', 'strike', 'triumph', 'mighty',
            'strength', 'overcome', 'prevail', 'stand firm', 'resist'
        ]
    
    def analyze_text(self, text):
        sentences = sent_tokenize(text)
        
        # Calculate average words per sentence
        words_per_sentence = [len(word_tokenize(sent)) for sent in sentences]
        avg_words = sum(words_per_sentence) / len(sentences)
        
        # Calculate short sentence ratio (sentences < 8 words)
        short_sentences = sum(1 for wps in words_per_sentence if wps < 8)
        short_ratio = short_sentences / len(sentences)
        
        # Count combat metaphors
        text_lower = text.lower()
        metaphor_count = sum(text_lower.count(metaphor) for metaphor in self.combat_metaphors)
        
        # Calculate match scores (0-1 scale)
        words_score = 1 - min(abs(avg_words - self.target_avg_words) / self.target_avg_words, 1)
        ratio_score = 1 - abs(short_ratio - self.target_short_ratio)
        metaphor_density = metaphor_count / (len(word_tokenize(text)) / 100)  # per 100 words
        
        return {
            'avg_words_per_sentence': avg_words,
            'short_sentence_ratio': short_ratio,
            'combat_metaphors_per_100': metaphor_density,
            'match_score': (words_score + ratio_score + min(metaphor_density/10, 1)) / 3
        }
    
    def get_voice_suggestions(self, text):
        stats = self.analyze_text(text)
        suggestions = []
        
        if stats['match_score'] < 0.7:
            if stats['avg_words_per_sentence'] > self.target_avg_words:
                suggestions.append("Consider breaking longer sentences into shorter ones")
            if stats['short_sentence_ratio'] < self.target_short_ratio:
                suggestions.append("Increase the number of short, punchy sentences")
            if stats['combat_metaphors_per_100'] < 2:
                suggestions.append("Add more combat/warrior metaphors for stronger impact")
                
        return suggestions