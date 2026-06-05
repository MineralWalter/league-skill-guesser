import streamlit as st
import json
import random
import os

st.set_page_config(page_title="League Skill Trivia", page_icon="🎮", layout="centered")
st.title("Guess the Champion by Skill Icon")

@st.cache_data
def load_data():
    with open("game_data.json", "r") as f:
        return json.load(f)

data = load_data()

champ_list = [""] + sorted(list(data.keys()))

if "score" not in st.session_state:
    st.session_state.score = 0
if "current_champ" not in st.session_state:
    random_champ_name = random.choice(list(data.keys()))
    st.session_state.current_champ = random_champ_name
    
    available_slots = [slot for slot, icons in data[random_champ_name].items() if icons and slot != "extras"]
    st.session_state.current_slot = random.choice(available_slots)
    
    st.session_state.current_icon = random.choice(data[random_champ_name][st.session_state.current_slot])

if "feedback" not in st.session_state:
    st.session_state.feedback = ""
if "feedback_type" not in st.session_state:
    st.session_state.feedback_type = None
if "stage" not in st.session_state:
    st.session_state.stage = "champ"

def next_question():
    random_champ_name = random.choice(list(data.keys()))
    st.session_state.current_champ = random_champ_name
    
    available_slots = [slot for slot, icons in data[random_champ_name].items() if icons and slot != "extras"]
    st.session_state.current_slot = random.choice(available_slots)
    st.session_state.current_icon = random.choice(data[random_champ_name][st.session_state.current_slot])
    
    st.session_state.feedback = ""
    st.session_state.feedback_type = None
    st.session_state.stage = "champ"

if st.session_state.feedback:
    if st.session_state.feedback_type == "error":
        st.error(st.session_state.feedback)
    elif st.session_state.feedback_type == "warning":
        st.warning(st.session_state.feedback)
    elif st.session_state.feedback_type == "success":
        st.success(st.session_state.feedback)

header_col1, header_col2, header_col3 = st.columns([1, 3, 1])

correct_name = st.session_state.current_champ
correct_slot = st.session_state.current_slot

# FIXEDD reconstruct path using champion folder and filename
img_path = os.path.join("cd_skill_icons", correct_name, st.session_state.current_icon)

with header_col1:
    if os.path.exists(img_path):
        st.image(img_path, width=90)
    else:
        st.error("Missing!")

with header_col2:
    st.subheader("Which champion ability is this?")

with header_col3:
    st.metric(label="Score", value=st.session_state.score)

st.write("---")

if st.session_state.stage == "champ":
    with st.form(key="guess_form", clear_on_submit=False):
        input_col1, input_col2 = st.columns([4, 1])
        
        with input_col1:
            user_guess = st.selectbox(
                "Select a champion:", 
                options=champ_list,
                index=0
            )
        
        with input_col2:
            if user_guess != "":
                preview_icon_path = os.path.join("league_champion_icons", f"{user_guess}.png")
                if os.path.exists(preview_icon_path):
                    st.image(preview_icon_path, width=50)

        submit_button = st.form_submit_button(label="Submit Guess")

    if submit_button:
        if user_guess == "":
            st.session_state.feedback = "⚠️ Please select a champion from the dropdown before submitting!"
            st.session_state.feedback_type = "warning"
            st.rerun()
        elif user_guess == correct_name:
            st.session_state.score += 1
            st.session_state.feedback = f"🎯 **Correct! It is {correct_name}.** Now, which ability slot is it?"
            st.session_state.feedback_type = "success"
            st.session_state.stage = "slot"
            st.rerun()
        else:
            st.session_state.feedback = f"❌ Wrong champion! Try again or Skip."
            st.session_state.feedback_type = "error"
            st.rerun()

    if st.button("Skip Champion ➡️"):
        st.session_state.feedback = f"🔍 The champion was **{correct_name}**. But can you guess the slot?"
        st.session_state.feedback_type = "warning"
        st.session_state.stage = "slot"
        st.rerun()

elif st.session_state.stage == "slot":
    slot_header_l, slot_header_r = st.columns([4, 1])
    with slot_header_l:
        st.info(f"Champion Identified: **{correct_name}**")
        st.write("Choose which ability this icon belongs to:")
    with slot_header_r:
        champ_face_path = os.path.join("league_champion_icons", f"{correct_name}.png")
        if os.path.exists(champ_face_path):
            st.image(champ_face_path, width=65)
    
    cols = st.columns(5)
    slots = ["Passive", "Q", "W", "E", "R"]
    
    for i, slot_name in enumerate(slots):
        # Convert to lowercase to match the JSON keys
        json_slot_key = slot_name.lower()
        with cols[i]:
            if st.button(f"{slot_name}", key=f"btn_{slot_name}", use_container_width=True):
                if json_slot_key == correct_slot:
                    st.session_state.score += 1
                    st.session_state.feedback_type = "success"
                    st.session_state.feedback = f"🎉 Correct, it's **{correct_name}**'s **{slot_name}** ability!"
                else:
                    st.session_state.feedback_type = "error"
                    st.session_state.feedback = f"Incorrect! The correct answer was **{correct_name}**'s **{correct_slot.upper()}** ability."
                st.session_state.stage = "complete"
                st.rerun()

    st.write("")
    if st.button("Skip ⏩"):
        st.session_state.feedback_type = "warning"
        st.session_state.feedback = f"The icon belongs to the **{correct_slot.upper()}** slot."
        st.session_state.stage = "complete"
        st.rerun()

elif st.session_state.stage == "complete":
    champ_face_path = os.path.join("league_champion_icons", f"{correct_name}.png")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if os.path.exists(champ_face_path):
            st.image(champ_face_path, width=70)
    with col2:
        st.markdown(f"### {correct_name}")
        st.caption(f"Mastery data logged for slot [{correct_slot.upper()}]")
        
    st.write("")
    if st.button("Next Round", icon=":material/arrow_forward:", use_container_width=True):
        next_question()
        st.rerun()

st.write("---")
st.caption("Made by Haru Nora | Discord: haru.nora")
# I hate using emotes bro