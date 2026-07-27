---
name: mud-player
description: Connect to, inspect, and play the local text MUD at localhost:4000 while preserving player and world memory across sessions. Use when asked to log in to the MUD, send MUD commands, explore its world, inspect game output, pursue multi-step goals such as gaining levels or defeating a monster, or update MUD progress.
---

# MUD Player

Use `scripts/mud.py` for every MUD connection. It defaults to the configured local server and the provided training account. Do not print or put the password in game commands, transcripts, or summaries.

## Persistent memory

Read `data/player.md` and `data/world.md` before every substantive MUD task. Use them to resume location, character progress, known routes, active goals, and previously verified facts.

Create or update an active-goal entry in `data/player.md` before starting a multi-step objective. Include the goal, target, current progress, blockers, and the next safe action. For example, record the current level and experience gap for a level goal, or record a target monster's known location, danger, and preparation for a combat goal.

After a meaningful action, update the memory with verified changes:

- Update `data/player.md` for character state, inventory, currency, practice sessions, skills, location, objectives, and progress.
- Update `data/world.md` for durable world facts such as routes, guilds, shops, commands, NPCs, monster locations, and combat observations.
- Mark uncertain or time-sensitive information as unverified rather than presenting it as fact.
- Preserve useful existing entries. Replace a stale value only after confirming the new value in MUD output.
- Never store credentials, full transcripts, or terminal-control noise.

Conclude each goal turn by recording the outcome and next action, so a later session can continue without rediscovering the same information.

## Run commands

Run one or more commands after logging in:

```bash
python3 scripts/mud.py --command look --command help
```

Pass a command exactly as the MUD expects. Keep command sequences short, inspect the output, then decide what to do next. Use `--commands-file path/to/commands.txt` for one command per line; blank lines and lines starting with `#` are ignored.

## Play interactively

Start an interactive session when exploration or a conversation needs back-and-forth control:

```bash
python3 scripts/mud.py --interactive
```

Type `/quit` to disconnect. The helper shows the server's initial text and output after each command.

## Connection controls

Override the target or account only when requested:

```bash
MUD_HOST=example.org MUD_PORT=4000 MUD_USERNAME=player MUD_PASSWORD=secret \
  python3 scripts/mud.py --command look
```

Use `--host`, `--port`, `--username`, and `--password` for one-off overrides. Prefer environment variables to avoid placing credentials in shell history. Use `--settle SECONDS` only if a slow server needs more time to respond.

The local server performs a delayed client-detection sequence before showing the login prompt. Let `scripts/mud.py` handle this prompt-driven login; do not replace it with a fixed sleep or send credentials before the prompt appears. The existing training account normally shows a password prompt after the username, and may print `Reconnecting.` immediately after successful authentication.

## Verified bakery workflow

Check the current room first because the character's location can change between sessions. In the verified training state, the character began in **The Bakery**. Use this safe discovery sequence to inspect it and list its stock:

```bash
python3 scripts/mud.py --command look --command 'read sign' --command list
```

The sign instructs the player to use `list` for prices and `buy` to purchase bread or pastry. The last verified list was:

- A danish pastry — 7
- A bread — 14
- A waybread — 73

Run `list` again before reporting prices or buying anything, since the game state may change. Ask for confirmation before using `buy`, because it spends currency.

## Safe play workflow

1. Begin with `look`, `help`, `score`, `inventory`, or similarly non-destructive discovery commands.
2. Preserve important location, quest, inventory, and combat details from the MUD's actual output; do not assume standard MUD vocabulary or map layout.
3. Before irreversible or costly actions (spending currency, dropping items, attacking, accepting a quest, or using a reset command), state the intended command and ask the user for confirmation unless they already authorized it.
4. Report the command sent, summarize the server response concisely, and update the memory files.
