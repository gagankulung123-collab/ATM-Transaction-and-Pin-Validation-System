# ATM Transaction and PIN Validation System

TECH 315 (Models of Computation) team project, King's College.

## About the Project
This project uses automata theory to model an ATM. A DFA checks the PIN
(3 attempts, then the card is locked). A PDA uses a stack to handle deposit,
withdrawal and balance check.

## Team Members
- Ajay Karki
- Adeen Bajra Bajracharya
- Gagan Rai

## Models Used
| Model | Purpose |
|-------|---------|
| DFA | Validates the 4-digit PIN with 3 attempts and a lock state |
| PDA | Handles deposit, withdraw and balance check using a stack |

## Diagrams
# DFA (PIN Validation)
<img width="2720" height="2000" alt="DFA" src="https://github.com/user-attachments/assets/65a7541f-c09a-4a67-b66c-1b8df9a0b8dd" />

# PDA 1: PIN Check Using a Stack
<img width="1600" height="731" alt="PIN validation check (PDA)" src="https://github.com/user-attachments/assets/94db88d6-939f-43e3-9130-e1ff57187766" />

# PDA 2: Transactions (Deposit, Withdraw, Balance Check)
<img width="713" height="537" alt="PDA" src="https://github.com/user-attachments/assets/2b56aa08-8718-4984-8f74-f2852db4687c" />

# System Flowchart
<img width="797" height="842" alt="Flowchart" src="https://github.com/user-attachments/assets/a390c77d-8cd2-42c9-93a6-5ddb3d75a9b9" />
