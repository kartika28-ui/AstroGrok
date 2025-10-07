# app.py
import os
from datetime import date, time as dtime
from textwrap import dedent
import streamlit as st
from dotenv import load_dotenv
from groq import Groq 


load_dotenv() 

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    client = None
    st.error("🚨 Missing GROQ_API_KEY! Please add it in your .env file.")

st.set_page_config(
    page_title="AstroGrok - AI-Powered Astrology Web App",
    page_icon="🔮",
    layout="centered",
)


st.markdown("""
<style>

.stApp {
  background: radial-gradient(1200px 600px at 20% 0%, #bda7ff40, transparent 60%),
              radial-gradient(1000px 500px at 100% 10%, #a6e3ff50, transparent 55%),
              linear-gradient(180deg, #0f1020 0%, #13142a 100%);
  color: #f5f6ff;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
}

h1, h2, h3 {
  text-shadow: 0 2px 20px rgba(170, 140, 255, 0.35);
  color: #fff;
}

input, textarea, select, .stDateInput, .stTimeInput {
  color: #000 !important;
}
.stTextInput > div > div > input,
.stDateInput input, .stTimeInput input {
  background: #ffffff !important;
  border-radius: 14px !important;
  
}


div.stButton > button {
    background-color: #23213b !important;  /* normal background */
    color: #ffffff !important;             /* normal text color */
    border: 1px solid #ffffff !important;
    border-radius: 50px;
    padding: 10px 24px;
    margin-top: 20px;
}

div.stButton > button:hover {
    background-color: #3a3890 !important; /* hover background */
    color: #ffffff !important;            /* hover text color */
}



.small { opacity: .8; font-size: .92rem; }
.foot { opacity: .7; font-size: .82rem; margin-top: .6rem; }
.badge {
  display: inline-block; padding: .2rem .6rem; border-radius: 999px;
  background: linear-gradient(90deg,#9b6bff,#4cc9f0); color: #0f1020; font-weight: 700;
}
            
[data-testid="stMarkdownContainer"] {
        color: white !important;
}
</style>
""", unsafe_allow_html=True)


ZODIAC_TRAITS = {
    "Aries": "Bold, action-oriented, competitive; great for kickstarting projects.",
    "Taurus": "Grounded, steady, sensual; values comfort, persistence, reliability.",
    "Gemini": "Curious, social, adaptable; excels at communication and learning.",
    "Cancer": "Nurturing, intuitive, protective; home and family are anchors.",
    "Leo": "Confident, expressive, generous; thrives when leading and creating.",
    "Virgo": "Detail-oriented, practical, service-driven; sharp at refining systems.",
    "Libra": "Diplomatic, harmonious, aesthetic; seeks balance and fair outcomes.",
    "Scorpio": "Intense, strategic, transformational; powerful focus and resilience.",
    "Sagittarius": "Adventurous, philosophical, optimistic; loves growth and travel.",
    "Capricorn": "Ambitious, disciplined, patient; builds long-term achievements.",
    "Aquarius": "Inventive, independent, humanitarian; forward-thinking and original.",
    "Pisces": "Empathic, imaginative, healing; creative and spiritually attuned.",
}

def zodiac_from_month_day(m: int, d: int) -> str:
    if   (m == 3  and d >= 21) or (m == 4  and d <= 19): return "Aries"
    if   (m == 4  and d >= 20) or (m == 5  and d <= 20): return "Taurus"
    if   (m == 5  and d >= 21) or (m == 6  and d <= 20): return "Gemini"
    if   (m == 6  and d >= 21) or (m == 7  and d <= 22): return "Cancer"
    if   (m == 7  and d >= 23) or (m == 8  and d <= 22): return "Leo"
    if   (m == 8  and d >= 23) or (m == 9  and d <= 22): return "Virgo"
    if   (m == 9  and d >= 23) or (m == 10 and d <= 22): return "Libra"
    if   (m == 10 and d >= 23) or (m == 11 and d <= 21): return "Scorpio"
    if   (m == 11 and d >= 22) or (m == 12 and d <= 21): return "Sagittarius"
    if   (m == 12 and d >= 22) or (m == 1  and d <= 19): return "Capricorn"
    if   (m == 1  and d >= 20) or (m == 2  and d <= 18): return "Aquarius"
    return "Pisces"

def soft_time_profile(t: dtime | None) -> str:
    if t is None:
        return "Balanced timing—trust your natural rhythm."
    mins = t.hour * 60 + t.minute
    if 300 <= mins < 720:   return "Morning-born: initiator energy & clear starts."
    if 720 <= mins < 1020:  return "Day-born: steady momentum & consistent build."
    if 1020 <= mins < 1260: return "Evening-born: reflective strength & social intuition."
    return "Night-born: deep intuition & creative focus when it’s quiet."

def base_reading(name: str, dob: date, tob: dtime | None, place: str, zodiac: str) -> str:
    first = (name or "You").split()[0]
    traits = ZODIAC_TRAITS.get(zodiac, "")
    timing = soft_time_profile(tob)
    return dedent(f"""
    **{first}, your Sun sign is _{zodiac}_**  
    • Core vibe: {traits}  
    • Timing tint: {timing}  
    • Place influence: *{place or 'your roots'}* highlights community and environment themes.

    **Weekly nudge:** Lean into your natural {zodiac.lower()} strengths while balancing them with patience and clear boundaries.
    """)


def groq_predict(payload: dict) -> str:
   
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not set")

    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)

    system = (
        "You are a friendly, grounded AI astrologer. "
        "Use western sun-sign basics and gentle timing nuance. "
        "Be practical, supportive, and non-fatalistic. Offer 2–3 concise, actionable tips."
    )
    user = dedent(f"""
    Birth details (no user question provided):
    - Name: {payload['name']}
    - DOB: {payload['dob']}
    - Time: {payload['tob']}
    - Place: {payload['place']}
    - Sun sign: {payload['zodiac']}

    Create a short, well-structured reading with sections:
    1) Personality snapshot
    2) Career/Work
    3) Relationships/Community
    4) Wellbeing
    End with a single empowering mantra line.
    """)

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.7,
        max_tokens=500,
    )
    return resp.choices[0].message.content.strip()

def offline_predict(zodiac: str) -> str:
    tip = (
        "Build small rituals that compound over weeks." if zodiac in {"Capricorn","Virgo","Taurus"} else
        "Say yes to a new idea or conversation today." if zodiac in {"Gemini","Libra","Aquarius"} else
        "Lead with compassion, then plan the steps." if zodiac in {"Cancer","Scorpio","Pisces"} else
        "Take a bold first step, then refine."
    )
    return f"*Offline mode:* Focus for {zodiac}: **{tip}**"



st.title("AI Astrologer")


with st.container():
    with st.form("astro_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full Name", placeholder="e.g., Aanya Sharma")
            dob = st.date_input("Date of Birth", value=None, min_value=date(1900,1,1))
            place = st.text_input("Birth Place (city, country)", placeholder="e.g., Mumbai, India")
        with c2:
            tob = st.time_input("Time of Birth (optional)", value=None, step=60)
            st.markdown('<div class="small">We’ll auto-generate your reading—no question needed.</div>', unsafe_allow_html=True)

        submitted = st.form_submit_button("Get My Reading")

    st.markdown('</div>', unsafe_allow_html=True)

if submitted:
    if not dob:
        st.error("Please select your Date of Birth.")
    else:
        zodiac = zodiac_from_month_day(dob.month, dob.day)
        st.markdown(
            f'<div class="glass"><span class="badge">Sun sign</span>  '
            f'&nbsp;{zodiac}✨</div>', unsafe_allow_html=True
        )

        st.subheader("Overview")
        st.markdown(base_reading(name, dob, tob, place, zodiac))

 
        payload = {
            "name": name or "Friend",
            "dob": dob.isoformat(),
            "tob": tob.strftime("%H:%M") if tob else "N/A",
            "place": place or "N/A",
            "zodiac": zodiac
        }

        st.subheader("Your Detailed Reading")
        try:
            if GROQ_API_KEY:
                with st.spinner("Consulting the cosmos…"):
                    ai_text = groq_predict(payload)
                st.markdown(ai_text)
            else:
                st.info("No GROQ_API_KEY detected — showing offline guidance.")
                st.markdown(offline_predict(zodiac))
        except Exception as e:
            st.warning(f"AI temporarily unavailable. Showing offline guidance.\n\n_{e}_")
            st.markdown(offline_predict(zodiac))

st.markdown('<div class="foot">For guidance only. Not a substitute for professional advice.</div>',
            unsafe_allow_html=True)
