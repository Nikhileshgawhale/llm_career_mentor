import streamlit as st
from mentor_bot import get_daily_plan, analyze_resume, ask_bot, log_daily_goal, log_interaction, load_memory, save_memory, set_resume, get_resume
from datetime import date, timedelta, datetime
import ollama
import pandas as pd
import random

st.set_page_config(page_title="LLM Career Mentor Bot", layout="wide")

# --- GAMER THEME COLORS ---
NEON_BLUE = "#00ffe7"
NEON_PINK = "#ff00c8"
NEON_PURPLE = "#a259ff"
DARK_BG = "#181a20"
DARK_CARD = "#23272f"
GLOW = f"0 0 16px {NEON_BLUE}, 0 0 32px {NEON_PINK}"

# Sidebar: Player Stats
sidebar = st.sidebar
sidebar.markdown(f"""
    <div style='background:linear-gradient(135deg,{NEON_PURPLE} 0%,{NEON_BLUE} 100%);padding:18px 10px 10px 10px;border-radius:18px;box-shadow:{GLOW};margin-bottom:18px;'>
        <h2 style='color:{NEON_PINK};text-shadow:{GLOW};text-align:center;'>🎮 Player Stats</h2>
    </div>""", unsafe_allow_html=True)

# Ollama status indicator
ollama_status = False
ollama_msg = ""
try:
    models = ollama.list()
    ollama_status = True
    model_names = []
    for m in models.get('models', []):
        if hasattr(m, 'model'):
            model_names.append(m.model)
        elif isinstance(m, dict) and 'model' in m:
            model_names.append(m['model'])
    ollama_msg = f"Ollama is running. Models: {', '.join(model_names)}"
except Exception as e:
    ollama_msg = f"Ollama is NOT running or not reachable: {e}"

sidebar.markdown(f"<div style='color:{NEON_BLUE};font-weight:bold;'>Ollama Status: {'🟢' if ollama_status else '🔴'}</div>", unsafe_allow_html=True)
sidebar.info(ollama_msg)

# Load memory and progress data
memory = load_memory()
today_str = date.today().isoformat()

# Progress chart and Solo Leveling-style progress in sidebar
streak = 0
streak_dates = []
if 'daily_goals' in memory:
    d = date.today()
    while True:
        d_str = d.isoformat()
        if d_str in memory['daily_goals'] and memory['daily_goals'][d_str].get('done'):
            streak += 1
            streak_dates.append(d_str)
            d -= timedelta(days=1)
        else:
            break
    all_dates = sorted(memory['daily_goals'].keys())
    progress_data = []
    for d in all_dates:
        done_val = 1 if memory['daily_goals'][d].get('done') else 0
        progress_data.append({'date': d, 'done': done_val})
    df = pd.DataFrame(progress_data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df.set_index('date', inplace=True)
    sidebar.markdown(f"<div style='color:{NEON_PINK};font-weight:bold;'>📈 Daily Completion Chart</div>", unsafe_allow_html=True)
    sidebar.line_chart(df['done'], height=120, use_container_width=True)
    total = len(df)
    completed = df['done'].sum()
    percent = int((completed / total) * 100) if total > 0 else 0
    # XP, Level, Badges
    level = streak // 7 + 1
    xp = streak * 10 + completed * 2
    next_level_xp = (level * 100)
    xp_percent = min(int((xp / next_level_xp) * 100), 100)
    sidebar.markdown(f"<div style='background:linear-gradient(90deg,{NEON_PINK},{NEON_BLUE});padding:10px;border-radius:10px;text-align:center;box-shadow:{GLOW};color:#fff;'><b>XP:</b> {xp} / {next_level_xp} <br><progress value='{xp}' max='{next_level_xp}' style='width:80%'></progress></div>", unsafe_allow_html=True)
    sidebar.markdown(f"<div style='background:{DARK_CARD};padding:10px;border-radius:10px;text-align:center;box-shadow:{GLOW};color:{NEON_BLUE};'><b>Level:</b> <span style='font-size:1.5em;'>{level}</span> {'⭐'*level}</div>", unsafe_allow_html=True)
    sidebar.progress(percent)
    # Badges
    if streak >= 30:
        sidebar.markdown(f"🏅 <span style='color:{NEON_PINK};text-shadow:{GLOW};'>30-Day Streak!</span>", unsafe_allow_html=True)
        st.snow()
        try:
            st.toast("Incredible! 30-Day Streak! ❄️", icon="🏅")
        except Exception:
            pass
    elif streak >= 7:
        sidebar.markdown(f"🥇 <span style='color:{NEON_BLUE};text-shadow:{GLOW};'>7-Day Streak!</span>", unsafe_allow_html=True)
    elif streak >= 3:
        sidebar.markdown(f"🥉 <span style='color:{NEON_PURPLE};text-shadow:{GLOW};'>3-Day Streak!</span>", unsafe_allow_html=True)
    sidebar.markdown(f"<div style='color:{NEON_PINK};font-weight:bold;'>Current Streak: {streak} day{'s' if streak != 1 else ''} :fire:</div>", unsafe_allow_html=True)
    if streak > 0:
        sidebar.success(f"You are getting stronger! Your streak is {streak} days. Like Solo Leveling, you are leveling up! Keep going!")
    else:
        sidebar.info("Start completing daily goals to begin your Solo Leveling journey!")
    # Celebration
    if streak and streak % 7 == 0:
        st.balloons()
        try:
            st.toast(f"Level Up! 🎉 You reached Level {level}", icon="⭐")
        except Exception:
            pass
    # Motivational quote
    quotes = [
        "Keep grinding, future AI master!",
        "Every day you level up, you get closer to your dream job!",
        "Consistency is your superpower.",
        "You're not just learning—you're evolving!",
        "Another day, another step towards mastery!",
        "You are the protagonist of your AI journey!"
    ]
    sidebar.info(random.choice(quotes))
else:
    sidebar.info("No progress yet. Complete your first daily goal!")

# Power-Up Button
if sidebar.button('⚡ Spin for Power-Up!'):
    powerup = random.choice([
        'Double XP for your next goal! ⚡',
        'Instant Level Up! 🚀',
        'Unlock a secret AI tip! 💡',
        'Bonus badge: Consistency Hero! 🏅',
        'Next chat answer will be supercharged! 🤖',
        'You get a motivational quote: "Push your limits!"',
    ])
    sidebar.success(f"Power-Up: {powerup}")
    try:
        st.toast(f"Power-Up: {powerup}", icon="⚡")
    except Exception:
        pass

# Daily Loot
if sidebar.button('🎁 Open Loot Box!'):
    loot = random.choice([
        'You gained +10 XP! 🎉',
        'You unlocked a new badge! 🏅',
        'You found a secret AI tip: Always document your experiments! 💡',
        'You earned a motivational quote: "Success is the sum of small efforts, repeated day in and day out."',
        'You received a power-up: Double XP for today! ⚡',
        'You discovered a hidden resource: https://arxiv.org/list/cs.AI/recent',
        'You got a rare drop: Free coffee coupon (in your dreams)! ☕',
        'You unlocked a new avatar! 🧑‍💻',
    ])
    sidebar.success(loot)
    try:
        st.toast(loot, icon="🎉")
    except Exception:
        pass

# Main area: Chat, Goals, Resources
st.markdown(f"<h1 style='color:{NEON_PINK};text-shadow:{GLOW};text-align:center;'>LLM Career Mentor Bot</h1>", unsafe_allow_html=True)

# Load resume from memory if available
resume_text = get_resume()

st.subheader("Resume")
if resume_text:
    st.success("Resume loaded from memory. You can update it below if needed.")
    st.markdown(f"**Current Resume:**\n\n{resume_text[:500]}{'...' if len(resume_text) > 500 else ''}")
else:
    st.info("No resume found. Please upload your resume.")

uploaded_resume = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt"])
if uploaded_resume:
    resume_text = analyze_resume(uploaded_resume)
    set_resume(resume_text)
    st.session_state['resume'] = resume_text
    st.success("Resume uploaded, saved, and analyzed!")

if 'resume' in st.session_state:
    resume_text = st.session_state['resume']

if resume_text:
    st.session_state['resume'] = resume_text

    if st.button("What should I do today?", help="Get your daily mission!"):
        daily_goal, resources, project_step = get_daily_plan(resume_text)
        log_daily_goal(today_str, daily_goal, resources, project_step)
        st.session_state['daily_goal'] = (daily_goal, resources, project_step)
        st.session_state['goal_generated'] = True

    # Show the most recent daily goal if available
    memory = load_memory()
    goal_data = None
    if today_str in memory.get('daily_goals', {}):
        goal_data = memory['daily_goals'][today_str]
    elif 'daily_goal' in st.session_state:
        daily_goal, resources, project_step = st.session_state['daily_goal']
        goal_data = {'goal': daily_goal, 'resources': resources, 'project_step': project_step}

    if goal_data:
        st.markdown("---")
        st.markdown(
            f"""<div style='background:linear-gradient(90deg,{NEON_PINK},{NEON_BLUE},{NEON_PURPLE});padding:24px 20px 20px 20px;border-radius:18px;margin-bottom:14px;box-shadow:{GLOW};'>
            <h2 style='color:{NEON_BLUE};text-shadow:{GLOW};font-size:2em;'>🏆 <span style='animation: bounce 1s infinite;'>Today's Mission</span></h2>
            <p style='font-size:1.3em;color:#fff;'>{goal_data['goal']} <span style='font-size:1.5em;'>🔥</span></p>
            </div>""", unsafe_allow_html=True
        )
        st.markdown(
            f"""<div style='background:linear-gradient(90deg,{NEON_BLUE},{NEON_PINK});padding:20px;border-radius:15px;margin-bottom:10px;box-shadow:{GLOW};'>
            <h3 style='color:{NEON_PINK};text-shadow:{GLOW};'>📚 <span style='animation: bounce 1s infinite;'>Recommended Resources</span></h3>
            {''.join([f'<li><a href="{r["url"]}" target="_blank" style="color:{NEON_BLUE};text-shadow:{GLOW};">{r["title"]}</a></li>' for r in goal_data['resources']]) if goal_data['resources'] else '<p style="color:#fff;">No resources found.</p>'}
            </div>""", unsafe_allow_html=True
        )
        st.markdown(
            f"""<div style='background:linear-gradient(90deg,{NEON_PURPLE},{NEON_PINK});padding:20px;border-radius:15px;margin-bottom:10px;box-shadow:{GLOW};'>
            <h3 style='color:{NEON_BLUE};text-shadow:{GLOW};'>🛠️ <span style='animation: bounce 1s infinite;'>Project Guidance</span></h3>
            <p style='font-size:1.1em;color:#fff;'>{goal_data['project_step']} <span style='font-size:1.3em;'>🚀</span></p>
            </div>""", unsafe_allow_html=True
        )
        st.markdown("---")

    # Mark goal as done
    done = False
    if 'daily_goals' in memory and today_str in memory['daily_goals']:
        done = memory['daily_goals'][today_str].get('done', False)
    done_checkbox = st.checkbox("Mission Complete! Mark today's goal as done", value=done)
    if done_checkbox != done:
        memory['daily_goals'][today_str]['done'] = done_checkbox
        save_memory(memory)
        st.balloons()
        try:
            st.toast("Mission Complete! Power-Up Unlocked! 🚀", icon="⚡")
        except Exception:
            pass

    # Chat section
    st.markdown(f"<h2 style='color:{NEON_PINK};text-shadow:{GLOW};'>Ask the Mentor Bot 💬</h2>", unsafe_allow_html=True)
    user_q = st.text_input("Your question")
    if user_q:
        answer = ask_bot(user_q, resume_text)
        log_interaction(today_str, user_q, answer)
        st.write(answer)

    # Persistent Chat History (like ChatGPT)
    st.markdown(f"<h2 style='color:{NEON_BLUE};text-shadow:{GLOW};'>Chat History 🗨️</h2>", unsafe_allow_html=True)
    if 'interactions' in memory:
        for d in sorted(memory['interactions'].keys(), reverse=True):
            st.markdown(f"<div style='color:{NEON_PINK};font-weight:bold;'>{d}</div>", unsafe_allow_html=True)
            for qa in memory['interactions'][d]:
                try:
                    with st.chat_message("user"):
                        st.write(qa['question'])
                    with st.chat_message("assistant"):
                        st.write(qa['answer'])
                except Exception:
                    st.markdown(f"**You:** {qa['question']}")
                    st.markdown(f"**Mentor Bot:** {qa['answer']}")
                    st.markdown("---")
    st.markdown("---")

    # Recent Progress (optional, can be removed if redundant)
    st.markdown(f"<h2 style='color:{NEON_PURPLE};text-shadow:{GLOW};'>Recent Progress 🕒</h2>", unsafe_allow_html=True)
    if 'daily_goals' in memory:
        st.markdown("**Past Daily Goals:**")
        for d, g in sorted(memory['daily_goals'].items(), reverse=True):
            status = "✅" if g.get('done') else "❌"
            st.markdown(f"- {d}: {g['goal']} {status}")
    if 'interactions' in memory and today_str in memory['interactions']:
        st.markdown("**Today's Q&A:**")
        for qa in memory['interactions'][today_str]:
            st.markdown(f"Q: {qa['question']}\n\nA: {qa['answer']}\n---") 