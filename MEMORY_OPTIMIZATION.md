# Memory Optimization Protocol

## The Problem
- Every session starts fresh
- Full context loading burns tokens
- Repeated information wastes processing

## The Solution: Selective Memory Loading

### 1. **Daily Memory Structure**
Instead of one giant MEMORY.md, use:
```
MEMORY.md                    # Core identity & critical info only (< 1000 words)
memory/YYYY-MM-DD.md        # Daily logs
memory/projects/            # Project-specific memory
memory/people/              # Relationship contexts
memory/systems/             # Established workflows
```

### 2. **Smart Loading Strategy**

#### On Session Start:
```
1. Read SOUL.md (who I am) - ALWAYS
2. Read USER.md (who you are) - ALWAYS  
3. Read today's memory/YYYY-MM-DD.md - ALWAYS
4. Read MEMORY.md - ONLY in main sessions
5. Project files - ONLY when working on that project
```

#### During Conversations:
```
Before answering about:
- Past decisions → memory_search "decision [topic]"
- Specific projects → memory_get "memory/projects/[project].md"
- People/relationships → memory_get "memory/people/[name].md"
- Established workflows → memory_get "memory/systems/[system].md"
```

### 3. **Token-Saving Rules**

**DON'T load everything** - Be surgical:
```bash
# BAD - loads entire file
Read MEMORY.md

# GOOD - loads only relevant section
memory_search "Gumroad revenue"
memory_get "MEMORY.md" from=47 lines=5
```

**Use memory markers**:
```markdown
<!-- SECTION: Gumroad Stats -->
Total revenue: $44,412.83
Last 28 days: $5,283.82
Top product: The Vault ($365)
<!-- END SECTION -->
```

### 4. **Context Pruning**

After loading memories, summarize and discard:
```
1. Load relevant memory section
2. Extract key facts needed
3. Answer the question
4. DON'T carry the full text forward
```

### 5. **Memory Writing Rules**

**Daily files** (memory/YYYY-MM-DD.md):
- Raw chronological logs
- Include context and decisions
- Can be verbose

**MEMORY.md updates**:
- Only distilled insights
- Remove outdated info
- Keep under 1000 words
- Use sections with clear headers

**Project files**:
- One file per major project
- Include current status at top
- Archive completed sections

### 6. **Search-First Approach**

Before loading any large file:
```
1. Try memory_search with specific query
2. Note which file and line numbers contain info
3. Use memory_get to extract ONLY those lines
4. Work with minimal context
```

### 7. **Automatic Cleanup**

During heartbeats:
- Review memory files for redundancy
- Move project-specific info to project files
- Archive old daily logs (>30 days)
- Update MEMORY.md with only essential info

## Implementation Checklist

- [ ] Split MEMORY.md into sections with markers
- [ ] Create memory/projects/ directory
- [ ] Create memory/people/ directory  
- [ ] Create memory/systems/ directory
- [ ] Move project-specific content to appropriate files
- [ ] Set up daily log rotation
- [ ] Document memory location map

## Token Savings Example

**Old way** (loads everything):
- MEMORY.md: 2,000 tokens
- Context window used: 2,000 tokens

**New way** (selective loading):
- memory_search "Gumroad": 50 tokens
- memory_get specific lines: 200 tokens
- Context window used: 250 tokens
- **Savings: 87.5%**

## Quick Reference

```bash
# Find something specific
memory_search "keyword or phrase"

# Get exact lines after search
memory_get "path/to/file.md" from=10 lines=5

# Check what's in memory without loading
ls -la memory/
ls -la memory/projects/
```

Remember: Every token saved is money saved and faster responses!