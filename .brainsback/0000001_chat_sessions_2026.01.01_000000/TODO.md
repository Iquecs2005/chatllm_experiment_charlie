# Strategic Blueprint

> Focus on the **what** and **why**. The code will follow.

**Hard rule**: AI agents must not edit this file and must not draft paste-ready content for it.

## The Problem
Create a side bar that will contain tabs with different chats with the ai. Each chat must have a unique title, if it doesnt one should be generetad based on the context. The user can create, delete and open these chats. Each chat is a different session and each of them has their own history.  

## Steps
- [X] Create the visual of the side bar and the tabs, with the corresponding buttons necessary for opening, creating and deleting tabs
- [X] Create the logic of manipulating the side bar
- [X] Integrate this logic with the visual
- [X] Create the logic on the backend necessary to hold multiple sessions of a user and the operations on these sessions, like: switching between them, deleting them, creating new ones and getting their history
- [X] Integrate the front with the backend
- [X] Create test for this feature

## Success Looks Like
- [X] The user is able to hold different session with the ai
- [X] The frontend enables this new features
- [X] All the created test passing

## Notes
- [X] Each session only has access to its own history, and cannot access other session history's
- [X] The tittle of each chat is assigned based on the initial message. Once that is set, the chat tittle should remain the same.

---
**⚠️ HUMAN ONLY**: This file is your strategic space. AI agents must not edit it.
