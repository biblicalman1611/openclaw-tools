from voice_dna_matcher import VoiceDNAMatcher
from kjv_reference_system import KJVReferenceSystem
from theme_categorizer import ThemeCategorizer

class ContentPipeline:
    def __init__(self):
        self.voice_matcher = VoiceDNAMatcher()
        self.scripture_system = KJVReferenceSystem()
        self.theme_categorizer = ThemeCategorizer()
    
    def process_content(self, content, scripture_refs=None):
        """
        Process content through the entire pipeline
        
        Args:
            content (str): The main content to process
            scripture_refs (list): Optional list of scripture references
            
        Returns:
            dict: Complete analysis results
        """
        results = {
            'voice_dna': self.voice_matcher.analyze_text(content),
            'voice_suggestions': self.voice_matcher.get_voice_suggestions(content),
            'themes': self.theme_categorizer.categorize_content(content),
            'scriptures': {}
        }
        
        # Process scripture references if provided
        if scripture_refs:
            for ref in scripture_refs:
                try:
                    verses = self.scripture_system.get_verses(ref)
                    results['scriptures'][ref] = verses
                except ValueError as e:
                    results['scriptures'][ref] = str(e)
        
        return results
    
    def validate_content(self, content, min_voice_score=0.7, min_theme_count=2):
        """
        Validate content against pipeline requirements
        
        Returns:
            tuple: (bool, list of issues)
        """
        issues = []
        voice_analysis = self.voice_matcher.analyze_text(content)
        theme_analysis = self.theme_categorizer.categorize_content(content)
        
        if voice_analysis['match_score'] < min_voice_score:
            issues.extend(self.voice_matcher.get_voice_suggestions(content))
            
        if len(theme_analysis['primary_themes']) < min_theme_count:
            issues.append(f"Content should strongly reflect at least {min_theme_count} core themes")
        
        return (len(issues) == 0, issues)

def main():
    # Example usage
    pipeline = ContentPipeline()
    
    sample_content = """
    Stand firm in the battle, mighty warrior of God! 
    Your identity is sealed in the blood of the Lamb.
    Take up your sword and shield, for victory awaits.
    """
    
    scripture_refs = ["Ephesians 6:10-11", "2 Timothy 4:7"]
    
    results = pipeline.process_content(sample_content, scripture_refs)
    is_valid, issues = pipeline.validate_content(sample_content)
    
    print("Content Analysis Results:")
    print("------------------------")
    print(f"Voice DNA Match Score: {results['voice_dna']['match_score']:.2f}")
    print(f"Primary Themes: {', '.join(results['themes']['primary_themes'])}")
    print("\nImprovement Suggestions:")
    for issue in issues:
        print(f"- {issue}")

if __name__ == "__main__":
    main()