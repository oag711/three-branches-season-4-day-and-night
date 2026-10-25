# Days at Three Branches agent

Edit `agent.py` to give every one of your villagers a routine. The platform runs a separate `Agent` instance for each NPC, so instances do not share variables or memory. The supplied `sandbox/` directory contains the local runner, types, and village helpers. Leave it unchanged, and leave `requirements.in` and `requirements.txt` alone: the pinned packages match the server.

Start with the [Getting Started guide](https://vox-deorum.github.io/game-sandbox/students/getting-started/). Then run these commands from this folder:

```console
python -m sandbox watch  # watch your villagers and the scripted visitor
python -m sandbox test   # run the checks
python -m sandbox eval   # run repeatable automated days
```

## Files you will use

| Path | Purpose |
| --- | --- |
| `agent.py` | Your `Agent` implementation and starter TODOs. |
| `environment.md` | Rules, helpers, observations, and local commands. |
| `manifest.json` | Tells Game Sandbox where the agent class lives. |
| `season.json` | Optional local season settings downloaded from My Submissions. |
| `tests/` | Checks your submission should pass. |
| `sandbox/` | Local game, helpers, and types. Do not edit it. |
| `requirements.txt` | Exact Python package versions used by the server. |
| `requirements-dev.txt` | Test dependencies. |
| `.env.example` | Example local LLM settings. |

The starter shows `action.walk`, `action.stand`, an emote, and `use`. Read [`environment.md`](environment.md) before changing it. Begin with one behavior that you can recognize in `watch`, then make it more responsive to the people and props it sees.

Chat is optional. If you add `chat(self, inbox)` to your agent, send and receive raw message dictionaries that use canonical player IDs such as `"player_0"` and `"player_1"`. For example, return `[{"to": "player_0", "text": "Hello."}]` to send a direct message. The village helpers do not include a chat namespace. Read [`environment.md`](environment.md#chat-with-other-agents) for the inbox format, broadcasts, and delivery timing.

In `watch` and `eval`, your `Agent` controls the whole cast, and `scripted_visitor` controls the visitor. The `naive` built-in is the simple baseline for the cast. When you are ready to submit, follow the [submitting guide](https://vox-deorum.github.io/game-sandbox/students/submitting/).

## Optional LLM API

If your instructor enables model calls, follow [Using the LLM API](llm.md). Copy `.env.example` to `.env`, add the endpoint and key, and never commit either secret.

Test the connection with:

```console
python -m sandbox llm
```

Design Goal

My goal for this project was to make the villagers have different jobs and routines throughout the day. I wanted each villager to have a specific place to go so that the village would feel more active and organized. For example, some villagers work at the pump, benches, crops, or crates, while other villagers visit different areas.

I also wanted the villagers to move around the village without getting stuck. To do this, I created a pathfinding system that searches for a route to each villager's target. I wanted the villagers to respond to the time of day by going to work, taking breaks, or heading home at night. I also added waving so the villagers could react when they see other people.

Design Reflection

One of the main challenges was making the villagers move to their correct destinations. I used a grid-based pathfinding system that checks nearby cells and finds a route toward the target. I also added a system that can rebuild a route if the villager has trouble moving along it. This helped me understand how pathfinding can be used to control characters in a game.

Another challenge was organizing the villagers' schedules. Each villager has a role, and their target can change depending on the phase of the day. I used conditions to decide where each villager should go during daytime, midday, evening, and night.

I think one strength of my design is that the villagers have different roles instead of all doing the same thing. However, the behavior could still be improved. Some villagers may gather near the same locations, and their routines could be more varied. In the future, I would like to spread the villagers out more, improve their daily schedules, and add conversations so they can tell each other what they are doing.

Overall, this project helped me understand how to use Python, conditions, functions, and pathfinding to create behavior for game characters.

AI-Use Disclosure and Reflection

I used ChatGPT to help me understand my code and work through programming problems. I used it as a tool to help explain ideas such as pathfinding, villager roles, and how the villagers change their behavior during different parts of the day.

Using AI helped me understand some programming concepts that were difficult for me at first. It also helped me identify possible problems and think about ways to improve the villagers' behavior. However, AI-generated suggestions still need to be checked because a solution may not work exactly as expected in the game.

This experience showed me that AI can be useful for learning and debugging, but I still need to understand the code, test it, and decide whether the changes improve my project. I used the assistance as a learning tool rather than assuming every suggestion was correct.