"""
mentor_bot.py: Core logic for LLM Career Mentor Bot
"""

import ollama
import json
import os
import re

MODEL_NAME = 'llama3'  # Change to your preferred local model
MEMORY_FILE = 'memory.json'

SYSTEM_PROMPT = (
    "You are an expert AI career mentor for LLM/GenAI engineers. "
    "Personalize advice, daily goals, and project guidance based on the user's resume and goals. "
    "Be concise, actionable, and reference top resources. "
    "Format your response in markdown with sections: ## Goal, ## Resources (as a markdown list with links), ## Project Step."
)

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return {}

def save_memory(memory):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory, f, indent=2)

def log_daily_goal(date_str, goal, resources, project_step):
    memory = load_memory()
    if 'daily_goals' not in memory:
        memory['daily_goals'] = {}
    memory['daily_goals'][date_str] = {
        'goal': goal,
        'resources': resources,
        'project_step': project_step
    }
    save_memory(memory)

def log_interaction(date_str, question, answer):
    memory = load_memory()
    if 'interactions' not in memory:
        memory['interactions'] = {}
    if date_str not in memory['interactions']:
        memory['interactions'][date_str] = []
    memory['interactions'][date_str].append({'question': question, 'answer': answer})
    save_memory(memory)

def analyze_resume(uploaded_file):
    """Extract text from uploaded resume file (stub)."""
    # TODO: Add PDF/DOCX/TXT parsing
    return "[Resume text extracted here]"

def get_daily_plan(resume_text):
    """Generate a daily goal, resources, and project step using Ollama LLM. Returns structured data."""
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"My resume: {resume_text}\n\nPlease set a daily goal, suggest 2-3 resources (with links), and give a project step for an aspiring AI Engineer focused on LLMs and GenAI."}
        ]
        response = ollama.chat(model=MODEL_NAME, messages=messages)
        content = response.message.content
        print("LLM raw output:", content)  # Debug print
        # Parse markdown sections
        goal = ""
        resources = []
        project_step = ""
        # Extract ## Goal
        goal_match = re.search(r"## Goal\s+(.+?)(?=##|$)", content, re.DOTALL)
        if goal_match:
            goal = goal_match.group(1).strip()
        # Extract ## Resources
        resources_match = re.search(r"## Resources\s+(.+?)(?=##|$)", content, re.DOTALL)
        if resources_match:
            resources_md = resources_match.group(1).strip()
            # Parse markdown links: [title](url)
            resources = re.findall(r"\[(.*?)\]\((.*?)\)", resources_md)
            resources = [{"title": t, "url": u} for t, u in resources]
        # Extract ## Project Step
        project_match = re.search(r"## Project Step\s+(.+?)(?=##|$)", content, re.DOTALL)
        if project_match:
            project_step = project_match.group(1).strip()
        return goal, resources, project_step
    except Exception as e:
        return f"[Error generating daily plan: {e}]", [], ""

def ask_bot(question, resume_text):
    """Answer user questions using Ollama LLM."""
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Resume: {resume_text}\n\nQuestion: {question}"}
        ]
        response = ollama.chat(model=MODEL_NAME, messages=messages)
        return response.message.content
    except Exception as e:
        return f"[Error from LLM: {e}]"

def set_resume(resume_text):
    memory = load_memory()
    memory['resume'] = resume_text
    save_memory(memory)

def get_resume():
    memory = load_memory()
    return memory.get('resume', None) 