1. An Agent file that defines the behavior of the agent. This file should contain the logic for how the agent will interact with the game world, including how it will explore, interact with objects and NPCs, and complete quests.

gpt-5.6-luna (reasoning high, summaries auto)

Observations:
- Coding Harness will read local files, not pertaining to the Loop. It will take it off task and waste credits. 
- The Agent current workspace is in the `week0_explore/explore_architecture/01_plain_agent` folder. The Agent should be able to read and write to the `data/player.md` and `data/world.md` files to remember the state of the game world and update the state of the game world each loop. The Agent should also be able to use the data in these files to make decisions about what actions to take in the game.
- During the Bakery run, the Agent did not read files outside the workspace. 

Key-Takeaway:
- Use coding harnesses for coding tasks. For a specialized operational agent, create a dedicated agent loop and reusable interface.
