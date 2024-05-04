<!-- Work in progress -->

# Red Teaming Targets

Queensland Government Customer and Digital Group (QGCDG) red teaming strategies for QChat bot

# Prerequisite
- Install python
- Install dependencies

# Output
- results folder

# Orchestration flow:
1. Generate malicious prompt with red teaming llm
2. Send malicious prompt
3. Receive target's response
4. Send response to scoring engine
5. Receive result from scoring engine
6. Generate new prompt based on scoring
7. Receive new malicious prompt from red teaming llm
-- REPEAT until EndToken or MaxTurns --

# Prompt flow
1. Send malicious prompt
2. Receive target's response
3. Send response to scoring engine
4. Receive result from scoring engine


## Safety alignment
- Policies alignment (brand reputation / values)
- Rule-breaking prompts (prompt going against policies)
- Generated prompts
- Accidental de-alignment (super helpful)

## Generic jailbreak
- Jailbreaking prompts (jailbreakchat.com)
- Generated custom jailbreak (create jailbreaks for specific contexts)
    + Jailbreak patterns (responsibility, character, research purposes, life or death, carrot or stick)
