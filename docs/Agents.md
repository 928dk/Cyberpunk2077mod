# Agents.md - Information for AI Agents

This document provides context for AI agents working on this Cyberpunk 2077 mod.

## Project: cp2077-merge-bypass

## Goal
Prevent V–Johnny merge in Relic storyline; fallback: inject alternative resolution to "get rid of JSH" while keeping other areas/quests accessible.

## Key Data
- Target test save: ManualSave-5 (pre-Heist, q004 done, q005 not done, 29.10.2022)
- Quests: q005_heist (The Heist), sq032_tapeworm (Tapeworm)
- Scene: sb_johnny_disappear (potential Path B hook)
- Fact: q302_06_johnny_disappear
- Save dir: $GAME_SAVED_GAMES/

## Tools Available
- CyberEngineTweaks (CET) - Lua hooks, runtime
- Redscript - core script overrides
- REDmod - modlet packaging
- WolvenKit - quest/scene extraction
- CyberpunkSaveEditor - save inspection
