import json
import re

class KJVReferenceSystem:
    def __init__(self):
        # Book name standardization
        self.book_mapping = {
            'gen': 'Genesis', 'exo': 'Exodus', 'lev': 'Leviticus',
            'num': 'Numbers', 'deu': 'Deuteronomy', 'jos': 'Joshua',
            'jdg': 'Judges', 'rut': 'Ruth', '1sa': '1 Samuel',
            '2sa': '2 Samuel', '1ki': '1 Kings', '2ki': '2 Kings',
            # ... (add all books)
        }
        
        # Cache for loaded verses
        self.verse_cache = {}
    
    def parse_reference(self, reference):
        """Parse a scripture reference (e.g., 'John 3:16' or 'Psalm 23:1-6')"""
        pattern = r'^(\d?\s*\w+)\s*(\d+):(\d+)(?:-(\d+))?$'
        match = re.match(pattern, reference)
        
        if not match:
            raise ValueError("Invalid reference format")
            
        book, chapter, start_verse, end_verse = match.groups()
        book = self.standardize_book_name(book)
        
        return {
            'book': book,
            'chapter': int(chapter),
            'start_verse': int(start_verse),
            'end_verse': int(end_verse) if end_verse else int(start_verse)
        }
    
    def standardize_book_name(self, book):
        """Convert various book name formats to standard KJV names"""
        book = book.lower().strip()
        book = re.sub(r'\s+', '', book)
        
        if book in self.book_mapping:
            return self.book_mapping[book]
        
        # Handle common variations
        for key, value in self.book_mapping.items():
            if book in value.lower().replace(' ', ''):
                return value
                
        raise ValueError(f"Unknown book: {book}")
    
    def get_verses(self, reference):
        """Retrieve verses from KJV text (implement caching for efficiency)"""
        ref_obj = self.parse_reference(reference)
        cache_key = f"{ref_obj['book']}_{ref_obj['chapter']}"
        
        if cache_key not in self.verse_cache:
            # Load verses from KJV source (implement actual loading logic)
            # self.verse_cache[cache_key] = load_chapter(ref_obj['book'], ref_obj['chapter'])
            pass
            
        verses = self.verse_cache[cache_key]
        return verses[ref_obj['start_verse']-1:ref_obj['end_verse']]
    
    def find_thematic_verses(self, theme):
        """Find verses related to a specific theme"""
        # Implement thematic search using pre-built index
        pass
    
    def get_cross_references(self, reference):
        """Get related cross-references for a verse"""
        # Implement cross-reference lookup
        pass