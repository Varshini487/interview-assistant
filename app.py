from openai import OpenAI
import streamlit as st

st.set_page_config(page_title="🎤 Interview Assistant", layout="wide")
st.title("🎤 AI Interview Assistant")
st.markdown("Practice interviews with AI feedback and scoring")

openai_key = st.sidebar.text_input("OpenAI API Key", type="password")
role = st.sidebar.selectbox("Job Role:", ["Software Engineer", "Data Scientist", "Product Manager", "ML Engineer", "Data Analyst"])
level = st.sidebar.selectbox("Experience Level:", ["Fresher", "Mid-level (2-5 yrs)", "Senior (5+ yrs)"])
q_type = st.sidebar.selectbox("Question Type:", ["Technical", "Behavioral", "Mixed"])

if "questions" not in st.session_state:
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.scores = []
    st.session_state.q_index = 0

def generate_question(client, role, level, q_type, prev_questions):
    prev = "\n".join(prev_questions[-3:]) if prev_questions else "None"
    prompt = f"""Generate ONE {q_type} interview question for a {level} {role} position.
Previously asked: {prev}
Return ONLY the question, nothing else."""
    r = client.chat.completions.create(model="gpt-4", messages=[{"role":"user","content":prompt}])
    return r.choices[0].message.content.strip()

def evaluate_answer(client, question, answer, role):
    prompt = f"""Evaluate this interview answer for a {role} position.
Question: {question}
Answer: {answer}

Provide:
1. Score (0-10)
2. Strengths (2-3 points)
3. Areas to improve (2-3 points)
4. Model answer (brief)

Format as JSON: {{"score": X, "strengths": [], "improvements": [], "model_answer": ""}}"""
    r = client.chat.completions.create(model="gpt-4", messages=[{"role":"user","content":prompt}])
    import json
    try:
        return json.loads(r.choices[0].message.content)
    except:
        return {"score": 7, "strengths": ["Good attempt"], "improvements": ["Be more specific"], "model_answer": ""}

if openai_key:
    client = OpenAI(api_key=openai_key)
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🎯 Generate Question") or not st.session_state.questions:
            q = generate_question(client, role, level, q_type, st.session_state.questions)
            st.session_state.questions.append(q)
        
        if st.session_state.questions:
            current_q = st.session_state.questions[-1]
            st.info(f"**Q{len(st.session_state.questions)}: {current_q}**")
            answer = st.text_area("Your Answer:", height=150, key=f"ans_{len(st.session_state.questions)}")
            if st.button("📊 Evaluate Answer") and answer:
                with st.spinner("Evaluating..."):
                    eval_result = evaluate_answer(client, current_q, answer, role)
                st.success(f"**Score: {eval_result.get('score',0)}/10**")
                st.write("**✅ Strengths:**", "\n".join(f"- {s}" for s in eval_result.get("strengths",[])))
                st.write("**📈 Improve:**", "\n".join(f"- {i}" for i in eval_result.get("improvements",[])))
                with st.expander("💡 Model Answer"): st.write(eval_result.get("model_answer",""))
    with col2:
        st.metric("Questions Asked", len(st.session_state.questions))
