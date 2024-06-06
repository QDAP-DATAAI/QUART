<!-- Work in progress -->

# Red Teaming Targets

Queensland Government Customer and Digital Group (QGCDG) red teaming strategies for QChat bot

# Prerequisite
- Install python 
- Install dependencies

# Guidline 
- Install python version 3.10 (requires admin access for installation on VMs).
- To get admin access, go to portal.azure.com navigate to Privilidged Identity Management-> Groups- DIS Cloud PC Local Admin, and under Eligible assignment, click  Activate and send a request.
- Download python from https://www.python.org/downloads/windows/ 
- Verify the version of the python to ensure it is 3.10 by running the command: `python --verison`.
- In main folder, run the command: `python -m pip install .` to install all dependencies (this may take a while).
- Install WSL by `wsl --install` (requires admin access for installation on VMs).
- Run the python files in the orchestration.
- Create the "results" folder (in Windows) at the root level.
- Make a connection in DBeaver (DuckDB) and open the file "red_teaming_data.db".
    - Note: You may need to close the conection whenever you want to run the code.

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
