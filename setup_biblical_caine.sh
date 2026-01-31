
cd /Users/thebi/voice-clone

# Create the enhanced Biblical Caine script
cat > scripts/biblical_caine.py << 'EOF'
#!/usr/bin/env python3
import sys
import os
import subprocess
from datetime import datetime

quotes = ['You were only supposed to blow the bloody doors off... of your marriage assumptions.', "Not many people know this, but grace is not for the deserving. It's for the desperate.", "My dear boy, you're performing Christianity like it's a West End show. But God's not in the audience - He's backstage, waiting for you to drop the act.", "Listen very carefully. Your wife doesn't need another sermon. She needs you to shut up and hold her while she cries.", 'Some men think leading means never showing weakness. Bollocks. Leading means bleeding in front of your family and letting them see you need God too.', "You know what's beautiful about being a grandfather? You get to see your failures become someone else's victories. That's grace, that is.", "Every morning at 4 AM, I'd sit in that freezing garbage truck and talk to God. Not because I was holy - because I was desperate. That's where real faith lives, son.", "Your son doesn't need you to be perfect. He needs you to be present. There's a bloody difference.", "Marriage isn't 50/50. It's 100/0, and sometimes you're the zero. That's when you find out if you actually believe what you preach.", "The algorithm is raising your sons while you're raising your metrics. Choose one. You already have."]

def create_caine_audio(text, filename=None):
    """Convert text to Michael Caine voice"""
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output/biblical_caine_{timestamp}.mp3"
    
    # Add Caine inflections
    caine_text = text.replace("you see", "you see, my dear boy,")
    caine_text = caine_text.replace("God", "God Almighty")
    
    try:
        # Using Oliver voice (British) as it's closer to Caine
        subprocess.run(["say", "-v", "Oliver", "-r", "170", "-o", filename, caine_text], check=True)
        print(f"✓ Created: {filename}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def create_all_samples():
    """Create all Biblical Caine samples"""
    for i, quote in enumerate(quotes):
        filename = f"output/biblical_caine_{i+1:02d}.mp3"
        print(f"\nCreating sample {i+1}/{len(quotes)}...")
        print(f"Quote: {quote[:50]}...")
        create_caine_audio(quote, filename)
    
    print("\n✓ All samples created in output/ directory")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        create_all_samples()
    elif len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        create_caine_audio(text)
    else:
        print("Usage: python biblical_caine.py 'Your text here'")
        print("   or: python biblical_caine.py --all  # Create all samples")
EOF

chmod +x scripts/biblical_caine.py

# Create a markdown doc with all quotes
cat > BIBLICAL_CAINE_QUOTES.md << 'EOF'
# Biblical Content in Michael Caine's Voice

Perfect for social media clips, podcast intros, or just having Michael Caine drop Biblical wisdom.

## The Quotes

1. "You were only supposed to blow the bloody doors off... of your marriage assumptions."

2. "Not many people know this, but grace is not for the deserving. It's for the desperate."

3. "My dear boy, you're performing Christianity like it's a West End show. But God's not in the audience - He's backstage, waiting for you to drop the act."

4. "Listen very carefully. Your wife doesn't need another sermon. She needs you to shut up and hold her while she cries."

5. "Some men think leading means never showing weakness. Bollocks. Leading means bleeding in front of your family and letting them see you need God too."

6. "You know what's beautiful about being a grandfather? You get to see your failures become someone else's victories. That's grace, that is."

7. "Every morning at 4 AM, I'd sit in that freezing garbage truck and talk to God. Not because I was holy - because I was desperate. That's where real faith lives, son."

8. "Your son doesn't need you to be perfect. He needs you to be present. There's a bloody difference."

9. "Marriage isn't 50/50. It's 100/0, and sometimes you're the zero. That's when you find out if you actually believe what you preach."

10. "The algorithm is raising your sons while you're raising your metrics. Choose one. You already have."

## How to Use

1. Generate a specific quote:
   ```bash
   cd ~/voice-clone
   python3 scripts/biblical_caine.py "Your custom Biblical wisdom here"
   ```

2. Generate all preset quotes:
   ```bash
   cd ~/voice-clone
   python3 scripts/biblical_caine.py --all
   ```

3. Find your audio files in `output/` directory

## Voice Settings
- Voice: Oliver (British English)
- Rate: 170 words per minute (slightly slower for gravitas)
- Format: MP3

## Pro Tips
- Add pauses with commas for dramatic effect
- Use "my dear boy" or "son" for that Caine touch
- End with "That's [concept], that is" for authentic Caine
EOF

echo "✓ Enhanced Biblical Caine voice system ready!"
echo "Run: python3 scripts/biblical_caine.py --all"

