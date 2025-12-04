# 🚀 Kaise Use Karein - Simple Guide

## Step 1: Terminal Kholo
```bash
# Current folder mein terminal kholo
# Ya command prompt mein jao:
cd D:\ABID\AI CODE EDITOR
```

## Step 2: Virtual Environment Activate Karo
```bash
venv\Scripts\activate
```

## Step 3: Chat Start Karo
```bash
python chat_agent.py
```

## Step 4: Chat Mein Type Karo

### Example 1: Current Folder Ki Files Modify Karo
```
💬 You: scan
# Ye dikhayega ki kaunsi files hain

💬 You: Add docstrings to test_calculator.py
# Ye automatically docstrings add kar dega
```

### Example 2: Kisi Aur Folder Ki Files Modify Karo
```
💬 You: project D:\MyProjects\WebApp
# Folder change ho jayega

💬 You: scan
# Us folder ki files dikhegi

💬 You: Add type hints to app.py
# Us folder ki file modify hogi
```

## Commands

| Type Karo | Kya Hoga |
|-----------|----------|
| `scan` | Saari files dikhegi |
| `project D:\Path` | Folder change hoga |
| `Add docstrings to file.py` | Docstrings add honge |
| `Add type hints to file.py` | Type hints add honge |
| `Fix TODO comments` | TODO fix honge |
| `help` | Help dikhega |
| `exit` | Band ho jayega |

## Complete Example

```bash
# 1. Start
python chat_agent.py

# 2. Dekho kya files hain
💬 You: scan

# 3. Koi file modify karo
💬 You: Add docstrings to test_calculator.py

# 4. Done! Exit karo
💬 You: exit
```

## Agar Error Aaye

Error ko copy karke chat mein paste karo:
```
💬 You: I got this error: [error paste karo]
```

## Real Example: Angular Todo App

```bash
# 1. Angular project banao
cd D:\
ng new angular-todo-app
cd angular-todo-app

# 2. Components banao
ng generate component components/todo-list
ng generate service services/todo

# 3. AI Agent start karo
cd D:\ABID\AI CODE EDITOR
venv\Scripts\activate
python chat_agent.py

# 4. Chat mein type karo
💬 You: project D:\angular-todo-app
💬 You: scan
💬 You: Add Todo interface in src/app/models/todo.interface.ts
💬 You: Add CRUD methods in src/app/services/todo.service.ts
💬 You: Add todo list display in todo-list component
```

📖 **Complete Angular example:** [ANGULAR_TODO_EXAMPLE.md](ANGULAR_TODO_EXAMPLE.md)

## That's It! 🎉

Bas itna hi! Simple hai:
1. `python chat_agent.py`
2. Type karo kya chahiye
3. Enter dabao
4. Done!
