"""Knowledge base: urgency levels, questions, IF-THEN rules and advice text."""

# ---------------------------------------------------------------------------
# Urgency levels
# ---------------------------------------------------------------------------

LEVELS = {
    4: {"key": "emergency", "label": "Emergency", "action": "Call your local emergency number now."},
    3: {"key": "urgent", "label": "Urgent", "action": "Get medical care today."},
    2: {"key": "soon", "label": "See a doctor soon", "action": "Book an appointment within 1–3 days."},
    1: {"key": "selfcare", "label": "Self-care at home", "action": "You can probably look after this at home."},
}

DISCLAIMER = (
    "This tool gives general guidance only. It is not a diagnosis and does not replace a doctor, "
    "nurse or emergency services. If you think it is an emergency, call your local emergency number "
    "(for example 911, 999 or 112) instead of using this checker."
)

# ---------------------------------------------------------------------------
# Knowledge base: questions
# ---------------------------------------------------------------------------
# type "single": pick one. type "multi": pick any; "none" is exclusive.
# `when`: conditions (same format as rule conditions) that must hold for the
# question to be asked. `complaint` is shorthand for a main-problem condition.

def _q(qid, short, text, qtype, options, why, complaint=None, when=None):
    conditions = ([("complaint", "is", complaint)] if complaint else []) + list(when or [])
    return {
        "id": qid, "short": short, "text": text, "type": qtype,
        "options": [{"value": v, "label": label} for v, label in options],
        "why": why, "when": conditions,
    }


QUESTIONS = [
    _q("redflags", "Danger signs", "Right now, do you have any of these?", "multi", [
        ("breathing", "Severe trouble breathing, or can't speak a full sentence"),
        ("chest", "Chest pain, pressure or tightness"),
        ("blue", "Blue or grey lips or face"),
        ("faint", "Fainted, can't be woken, or sudden confusion"),
        ("stroke", "Sudden face drooping, arm or leg weakness, or slurred speech"),
        ("bleeding", "Heavy bleeding that won't stop with firm pressure"),
        ("seizure", "A seizure (fit) now or just now"),
        ("allergy", "Swelling of lips, face or tongue, or throat tightness after a sting, food or medicine"),
        ("selfharm", "Thoughts of harming yourself or someone else"),
        ("none", "None of these"),
    ], "Some problems are dangerous whatever else is going on, so they are checked first. "
       "If you choose any of them, the questions stop and you are told what to do straight away."),

    _q("age", "Age group", "How old is the person who needs advice?", "single", [
        ("baby_u3m", "Under 3 months"),
        ("baby", "3 to 11 months"),
        ("child", "1 to 12 years"),
        ("adult", "13 to 64 years"),
        ("senior", "65 or older"),
    ], "Age changes how serious the same symptom is. For example, a fever in a very young baby "
       "is treated far more cautiously than in an adult."),

    _q("complaint", "Main problem", "What is the main problem?", "single", [
        ("fever", "Fever, or feeling feverish"),
        ("cough", "Cough or a breathing problem"),
        ("throat", "Sore throat or cold"),
        ("headache", "Headache"),
        ("stomach", "Stomach upset (vomiting, diarrhea, belly pain)"),
        ("other", "Something else"),
    ], "The main problem decides which follow-up questions are relevant, so you are not asked about "
       "things that don't apply."),

    _q("risk", "Higher-risk condition",
       "Does any of this apply? A long-term illness (heart, lung, kidney, diabetes), a weakened "
       "immune system (for example chemotherapy, steroids or a transplant), or pregnancy.",
       "single", [("yes", "Yes"), ("no", "No")],
       "Some conditions make infections and other problems riskier, so the same symptoms may need "
       "care sooner."),

    # ── Fever ──────────────────────────────────────────────────────────────
    _q("temp", "Highest temperature", "What is the highest temperature so far?", "single", [
        ("under38", "Under 38 °C (100.4 °F)"),
        ("t38", "38 to 38.9 °C (100.4 to 102 °F)"),
        ("t39", "39 to 39.9 °C (102.1 to 103.8 °F)"),
        ("t40", "40 °C (104 °F) or higher"),
        ("unknown", "Not measured, but feels hot"),
    ], "How high the fever is helps judge how seriously the body is reacting.", "fever"),
    _q("fever_days", "Fever length", "How long has the fever lasted?", "single", [
        ("d0", "Less than 1 day"),
        ("d1_3", "1 to 3 days"),
        ("d3p", "More than 3 days"),
    ], "A fever that lasts is more likely to need a check than one that has just started.", "fever"),
    _q("fever_sx", "Fever warning signs", "Any of these with the fever?", "multi", [
        ("stiff", "Stiff neck, or pain when looking at bright light"),
        ("rash", "A rash that does not fade when a glass is pressed on it"),
        ("drowsy", "Very drowsy, floppy or hard to wake"),
        ("vomit", "Repeated vomiting, can't keep fluids down"),
        ("urine", "Pain or burning when passing urine"),
        ("none", "None of these"),
    ], "These signs can mean a fever is more than a simple infection, so they raise the urgency.", "fever"),

    # ── Cough / breathing ──────────────────────────────────────────────────
    _q("choking", "Sudden start", "Did the cough start suddenly while eating or playing with small objects?", "single", [
        ("yes", "Yes, it started suddenly"),
        ("no", "No"),
    ], "In young children a sudden cough while eating or playing can mean something is stuck in the airway, "
       "which needs different handling from an ordinary cough.", "cough", [("age", "in", ["baby_u3m", "baby", "child"])]),
    _q("cough_breath", "Breathing", "How is your breathing?", "single", [
        ("normal", "Normal"),
        ("exert", "A bit short of breath when active or climbing stairs"),
        ("rest", "Short of breath even at rest or while talking"),
    ], "Breathlessness is one of the strongest signs that a cough needs attention.", "cough"),
    _q("cough_days", "Cough length", "How long have you had the cough?", "single", [
        ("lt1w", "Under 1 week"),
        ("w1_3", "1 to 3 weeks"),
        ("w3p", "More than 3 weeks"),
    ], "Most coughs from colds fade within about 3 weeks. A longer cough should be checked.", "cough"),
    _q("cough_sx", "Cough warning signs", "Any of these?", "multi", [
        ("blood", "Coughing up blood"),
        ("wheeze", "Wheezing or a whistling sound when breathing"),
        ("fever", "Fever of 38 °C (100.4 °F) or higher"),
        ("chestpain", "Chest pain when breathing in or coughing"),
        ("none", "None of these"),
    ], "These signs change how urgently a cough should be looked at.", "cough"),

    # ── Sore throat / cold ─────────────────────────────────────────────────
    _q("throat_sx", "Throat warning signs", "Any of these?", "multi", [
        ("drool", "Can't swallow your own saliva, or drooling"),
        ("muffled", "Muffled voice, or can't open your mouth fully"),
        ("fever", "High fever (38.5 °C / 101.3 °F or more) and no cough"),
        ("patches", "White patches or pus on the tonsils"),
        ("none", "None of these"),
    ], "A few throat symptoms point to problems that need a clinician, not just rest.", "throat"),
    _q("throat_days", "Throat length", "How long has the sore throat lasted?", "single", [
        ("lt1w", "Less than a week"),
        ("w1p", "A week or more"),
    ], "Sore throats from colds usually settle within a week.", "throat"),

    # ── Headache ───────────────────────────────────────────────────────────
    _q("ha_onset", "Headache start", "How did the headache start?", "single", [
        ("thunder", "Suddenly: the worst headache of my life, peaking within a minute"),
        ("gradual", "Gradually, over hours or days"),
    ], "A sudden, severe 'thunderclap' headache is treated as an emergency.", "headache"),
    _q("ha_sx", "Headache warning signs", "Any of these?", "multi", [
        ("injury", "It started after a blow to the head"),
        ("vision", "Vision changes: blurred, double or lost vision"),
        ("vomit", "Repeated vomiting"),
        ("neck", "Fever and a stiff neck"),
        ("worse", "Pain getting steadily worse over days or weeks, or waking me at night"),
        ("none", "None of these"),
    ], "These are the headache features that doctors want to see sooner rather than later.", "headache"),
    _q("ha_known", "Familiar headache", "Have you had headaches like this before?", "single", [
        ("yes", "Yes, similar to before"),
        ("no", "No, this feels new or different"),
    ], "A new kind of headache is judged differently from one you already know.", "headache"),

    # ── Stomach ────────────────────────────────────────────────────────────
    _q("gi_sx", "Stomach warning signs", "Any of these?", "multi", [
        ("bloodgi", "Vomiting blood, or black or bloody stools"),
        ("hard", "A very swollen, hard or rigid belly"),
        ("severe", "Severe belly pain that is constant or getting worse"),
        ("rlq", "Pain low on the right side of the belly, with fever"),
        ("dehyd", "Dehydration: very dry mouth, little or no urine in 8 hours, dizzy when standing"),
        ("none", "None of these"),
    ], "These signs separate a common stomach upset from something needing care.", "stomach"),
    _q("gi_fluids", "Keeping fluids down", "Can you keep fluids down?", "single", [
        ("yes", "Yes"),
        ("no", "No, I vomit most fluids"),
    ], "Not being able to keep fluids down leads to dehydration, especially in the young and old.", "stomach"),
    _q("gi_days", "Stomach length", "How long have the symptoms lasted?", "single", [
        ("lt2", "Less than 2 days"),
        ("d2_7", "2 to 7 days"),
        ("d7p", "More than 7 days"),
    ], "Most stomach upsets pass within a couple of days.", "stomach"),

    # ── Course of the illness, any of the five problems ────────────────────
    _q("trend", "Trend", "Over the last day, how have the symptoms changed?", "single", [
        ("better", "Getting better"),
        ("same", "About the same"),
        ("worse", "Getting worse"),
        ("rapid", "Getting worse quickly, over hours"),
    ], "Symptoms that are getting worse need a different response from ones that are settling.", None,
       [("complaint", "in", ["fever", "cough", "throat", "headache", "stomach"])]),
    _q("medicine", "Medicine taken", "Have you taken a fever or pain medicine (such as paracetamol or ibuprofen) for this?", "single", [
        ("no", "No"),
        ("helped", "Yes, and it helped"),
        ("nohelp", "Yes, but it did not help much"),
    ], "A fever or pain that does not respond to medicine is more likely to need a clinician.", None,
       [("complaint", "in", ["fever", "headache"])]),

    # ── Young children, any of the five problems ───────────────────────────
    _q("feeding", "Drinking or feeding", "Is the child drinking or feeding normally?", "single", [
        ("normal", "Yes, as usual"),
        ("less", "Less than usual"),
        ("refusing", "Refusing most drinks or feeds, or far fewer wet nappies or trips to the toilet"),
    ], "Babies and young children become dehydrated much faster than adults, so how well they are drinking "
       "is one of the most important signs.", None,
       [("age", "in", ["baby_u3m", "baby", "child"]), ("complaint", "in", ["fever", "cough", "throat", "headache", "stomach"])]),

]

QUESTION_BY_ID = {q["id"]: q for q in QUESTIONS}

# ---------------------------------------------------------------------------
# Knowledge base: rules
# ---------------------------------------------------------------------------
# A rule is: id, level, if (list of conditions, ALL must hold), reason.
# A condition is (fact, operator, value):
#   "is"    answer equals value
#   "in"    answer is one of the values
#   "has"   a multi-answer contains any of the values
#   "lacks" a multi-answer contains none of the values
# Every complaint has a level-1 baseline rule, so there is always a conclusion.

YOUNG = ["baby_u3m", "baby", "child"]
BABIES = ["baby_u3m", "baby"]
GROWN = ["adult", "senior"]
FEVER_38 = ["t38", "t39", "t40", "unknown"]


def _r(rid, level, conditions, reason):
    return {"id": rid, "level": level, "if": conditions, "reason": reason}


RULES = [
    # ── Danger signs (any age, any problem) ────────────────────────────────
    _r("RF1", 4, [("redflags", "has", ["breathing"])], "Severe trouble breathing can become life-threatening quickly."),
    _r("RF2", 4, [("redflags", "has", ["chest"])], "Chest pain, pressure or tightness can be a sign of a heart problem and needs emergency assessment."),
    _r("RF3", 4, [("redflags", "has", ["blue"])], "Blue or grey lips or face can mean the body is not getting enough oxygen."),
    _r("RF4", 4, [("redflags", "has", ["faint"])], "Fainting, being unable to wake, or sudden confusion needs emergency help."),
    _r("RF5", 4, [("redflags", "has", ["stroke"])], "Sudden face drooping, limb weakness or slurred speech can be signs of a stroke. Minutes matter."),
    _r("RF6", 4, [("redflags", "has", ["bleeding"])], "Heavy bleeding that will not stop with firm pressure needs emergency help."),
    _r("RF7", 4, [("redflags", "has", ["seizure"])], "A seizure needs emergency assessment, especially a first one or one lasting over 5 minutes."),
    _r("RF8", 4, [("redflags", "has", ["allergy"])], "Swelling of the lips, face or tongue, or throat tightness, can be a severe allergic reaction."),
    _r("RF9", 4, [("redflags", "has", ["selfharm"])], "You may be at risk of harm. Please contact emergency services or a crisis line now; you do not have to face this alone."),

    # ── Fever ──────────────────────────────────────────────────────────────
    _r("F1", 4, [("complaint", "is", "fever"), ("age", "is", "baby_u3m"), ("temp", "in", FEVER_38)],
       "A fever of 38 °C or more in a baby under 3 months needs an emergency assessment, even if the baby looks well."),
    _r("F2", 3, [("complaint", "is", "fever"), ("age", "is", "baby_u3m")],
       "Any sign of fever in a baby under 3 months should be checked by a clinician today."),
    _r("F3", 3, [("complaint", "is", "fever"), ("age", "is", "baby"), ("temp", "in", ["t39", "t40", "unknown"])],
       "A high or unmeasured fever in a baby aged 3 to 11 months should be checked today."),
    _r("F4", 2, [("complaint", "is", "fever"), ("age", "is", "baby"), ("temp", "is", "t38")],
       "A fever in a baby aged 3 to 11 months should be checked by a doctor soon."),
    _r("F5", 4, [("complaint", "is", "fever"), ("fever_sx", "has", ["stiff", "rash"])],
       "A stiff neck, light sensitivity or a rash that does not fade, together with fever, can be signs of a serious infection that needs emergency care."),
    _r("F6", 4, [("complaint", "is", "fever"), ("age", "in", YOUNG), ("fever_sx", "has", ["drowsy"])],
       "A feverish child or baby who is very drowsy, floppy or hard to wake needs emergency care."),
    _r("F7", 3, [("complaint", "is", "fever"), ("age", "in", GROWN), ("fever_sx", "has", ["drowsy"])],
       "Being very drowsy with a fever should be assessed by a clinician today."),
    _r("F8", 3, [("complaint", "is", "fever"), ("temp", "is", "t40")],
       "A temperature of 40 °C or higher should be assessed today."),
    _r("F9", 3, [("complaint", "is", "fever"), ("fever_sx", "has", ["vomit"]), ("age", "in", YOUNG + ["senior"])],
       "Repeated vomiting with a fever risks dehydration, which is more dangerous in the very young and the elderly."),
    _r("F10", 2, [("complaint", "is", "fever"), ("fever_sx", "has", ["vomit"]), ("age", "is", "adult")],
       "Repeated vomiting with a fever can lead to dehydration and should be checked soon."),
    _r("F11", 3, [("complaint", "is", "fever"), ("risk", "is", "yes"), ("temp", "in", FEVER_38)],
       "A fever with a long-term illness, a weakened immune system or pregnancy should be assessed today."),
    _r("F12", 3, [("complaint", "is", "fever"), ("age", "is", "senior"), ("temp", "in", ["t39", "t40"])],
       "A high fever in someone aged 65 or older should be assessed today."),
    _r("F13", 2, [("complaint", "is", "fever"), ("age", "is", "senior"), ("temp", "is", "t38")],
       "A fever in someone aged 65 or older should be checked soon."),
    _r("F14", 2, [("complaint", "is", "fever"), ("age", "is", "child"), ("temp", "in", ["t39", "t40"])],
       "A high fever in a child should be checked by a doctor soon if it does not settle."),
    _r("F15", 2, [("complaint", "is", "fever"), ("fever_days", "is", "d3p")],
       "A fever lasting more than 3 days should be checked."),
    _r("F16", 2, [("complaint", "is", "fever"), ("fever_sx", "has", ["urine"])],
       "Pain or burning when passing urine with a fever can mean an infection that needs treatment."),
    _r("F0", 1, [("complaint", "is", "fever")],
       "Fever on its own is common with infections and often settles with rest and fluids."),

    # ── Cough / breathing ──────────────────────────────────────────────────
    _r("C1", 3, [("complaint", "is", "cough"), ("cough_breath", "is", "rest")],
       "Being short of breath at rest or while talking should be assessed today."),
    _r("C2", 3, [("complaint", "is", "cough"), ("cough_sx", "has", ["blood"])],
       "Coughing up blood should be assessed today."),
    _r("C3", 3, [("complaint", "is", "cough"), ("age", "in", YOUNG), ("cough_sx", "has", ["wheeze"])],
       "Wheezing in a baby or child should be assessed today."),
    _r("C4", 2, [("complaint", "is", "cough"), ("age", "in", GROWN), ("cough_sx", "has", ["wheeze"])],
       "Wheezing should be checked by a doctor soon."),
    _r("C5", 3, [("complaint", "is", "cough"), ("age", "is", "baby_u3m")],
       "A cough in a baby under 3 months should be checked today."),
    _r("C6", 3, [("complaint", "is", "cough"), ("age", "is", "baby"), ("cough_breath", "in", ["exert", "rest"])],
       "Breathing difficulty with a cough in a baby should be checked today."),
    _r("C7", 2, [("complaint", "is", "cough"), ("cough_breath", "is", "exert")],
       "Being short of breath when active should be checked soon."),
    _r("C8", 2, [("complaint", "is", "cough"), ("cough_days", "is", "w3p")],
       "A cough lasting more than 3 weeks should be checked."),
    _r("C9", 3, [("complaint", "is", "cough"), ("risk", "is", "yes"), ("cough_sx", "has", ["fever"])],
       "A cough with fever and a long-term illness, weakened immune system or pregnancy should be assessed today."),
    _r("C10", 2, [("complaint", "is", "cough"), ("cough_sx", "has", ["chestpain"])],
       "Chest pain when breathing or coughing should be checked soon."),
    _r("C11", 2, [("complaint", "is", "cough"), ("cough_sx", "has", ["fever"]), ("cough_days", "in", ["w1_3", "w3p"])],
       "A cough with fever lasting over a week should be checked."),
    _r("C0", 1, [("complaint", "is", "cough")],
       "Most coughs come from colds and clear up on their own within about 3 weeks."),

    _r("C12", 3, [("complaint", "is", "cough"), ("choking", "is", "yes")],
       "A cough that started suddenly while eating or playing with small objects can mean something is stuck in the airway and should be assessed today."),

    # ── Sore throat / cold ─────────────────────────────────────────────────
    _r("S1", 4, [("complaint", "is", "throat"), ("throat_sx", "has", ["drool"])],
       "Being unable to swallow saliva, or drooling, can mean the airway is at risk and needs emergency care."),
    _r("S2", 3, [("complaint", "is", "throat"), ("throat_sx", "has", ["muffled"])],
       "A muffled voice or being unable to open the mouth fully should be assessed today."),
    _r("S3", 3, [("complaint", "is", "throat"), ("risk", "is", "yes"), ("throat_sx", "has", ["fever"])],
       "A high fever with a sore throat and a higher-risk condition should be assessed today."),
    _r("S4", 2, [("complaint", "is", "throat"), ("throat_sx", "has", ["fever"])],
       "A high fever with a sore throat and no cough should be checked soon."),
    _r("S5", 2, [("complaint", "is", "throat"), ("throat_sx", "has", ["patches"])],
       "White patches or pus on the tonsils should be checked soon."),
    _r("S6", 2, [("complaint", "is", "throat"), ("throat_days", "is", "w1p")],
       "A sore throat lasting a week or more should be checked."),
    _r("S0", 1, [("complaint", "is", "throat")],
       "Most sore throats come from colds and settle within a week."),

    # ── Headache ───────────────────────────────────────────────────────────
    _r("H1", 4, [("complaint", "is", "headache"), ("ha_onset", "is", "thunder")],
       "A sudden, severe 'worst ever' headache needs emergency assessment."),
    _r("H2", 4, [("complaint", "is", "headache"), ("ha_sx", "has", ["neck"])],
       "A headache with fever and a stiff neck can be a sign of a serious infection and needs emergency care."),
    _r("H3", 3, [("complaint", "is", "headache"), ("ha_sx", "has", ["injury"])],
       "A headache after a blow to the head should be assessed today."),
    _r("H4", 3, [("complaint", "is", "headache"), ("ha_sx", "has", ["vision"])],
       "A headache with vision changes should be assessed today."),
    _r("H5", 3, [("complaint", "is", "headache"), ("ha_sx", "has", ["vomit"])],
       "A headache with repeated vomiting should be assessed today."),
    _r("H6", 2, [("complaint", "is", "headache"), ("ha_sx", "has", ["worse"])],
       "A headache that keeps getting worse, or wakes you at night, should be checked soon."),
    _r("H7", 2, [("complaint", "is", "headache"), ("ha_known", "is", "no"), ("age", "is", "senior")],
       "A new kind of headache at 65 or older should be checked soon."),
    _r("H8", 2, [("complaint", "is", "headache"), ("ha_known", "is", "no"), ("risk", "is", "yes")],
       "A new kind of headache with a higher-risk condition should be checked soon."),
    _r("H0", 1, [("complaint", "is", "headache")],
       "Most headaches are tension-type or migraine-type and ease with rest, fluids and pain relief."),

    # ── Stomach upset ──────────────────────────────────────────────────────
    _r("G1", 4, [("complaint", "is", "stomach"), ("gi_sx", "has", ["bloodgi"])],
       "Vomiting blood, or black or bloody stools, can mean serious bleeding and needs emergency care."),
    _r("G2", 4, [("complaint", "is", "stomach"), ("gi_sx", "has", ["hard"])],
       "A very swollen, hard belly needs emergency assessment."),
    _r("G3", 3, [("complaint", "is", "stomach"), ("gi_sx", "has", ["severe"])],
       "Severe belly pain that is constant or getting worse should be assessed today."),
    _r("G4", 3, [("complaint", "is", "stomach"), ("gi_sx", "has", ["rlq"])],
       "Pain low on the right side with fever should be assessed today."),
    _r("G5", 3, [("complaint", "is", "stomach"), ("gi_sx", "has", ["dehyd"])],
       "Signs of dehydration should be assessed today."),
    _r("G6", 3, [("complaint", "is", "stomach"), ("gi_fluids", "is", "no"), ("age", "in", YOUNG + ["senior"])],
       "Not keeping fluids down risks dehydration, which is more dangerous in the very young and the elderly."),
    _r("G7", 3, [("complaint", "is", "stomach"), ("gi_fluids", "is", "no"), ("risk", "is", "yes")],
       "Not keeping fluids down with a higher-risk condition should be assessed today."),
    _r("G8", 2, [("complaint", "is", "stomach"), ("gi_fluids", "is", "no"), ("age", "is", "adult")],
       "Not keeping fluids down should be checked soon."),
    _r("G9", 3, [("complaint", "is", "stomach"), ("age", "is", "baby_u3m")],
       "Vomiting, diarrhea or belly pain in a baby under 3 months should be checked today."),
    _r("G10", 2, [("complaint", "is", "stomach"), ("gi_days", "is", "d7p")],
       "Stomach symptoms lasting more than a week should be checked."),
    _r("G11", 2, [("complaint", "is", "stomach"), ("gi_days", "is", "d2_7"), ("age", "in", ["baby", "child", "senior"])],
       "Stomach symptoms lasting more than 2 days in a baby, child or older adult should be checked."),
    _r("G0", 1, [("complaint", "is", "stomach")],
       "Most stomach upsets pass within a couple of days with fluids and rest."),

    # ── Young children: drinking and feeding ───────────────────────────────
    _r("D1", 3, [("age", "in", YOUNG), ("feeding", "is", "refusing")],
       "A baby or child who is refusing most drinks or feeds, or passing much less urine, is at risk of dehydration and should be assessed today."),
    _r("D2", 2, [("age", "in", BABIES), ("feeding", "is", "less")],
       "A baby who is feeding less than usual should be checked by a doctor soon."),

    # ── Course of the illness ──────────────────────────────────────────────
    _r("T1", 3, [("trend", "is", "rapid")],
       "Symptoms that are getting worse quickly, over hours, should be assessed today."),
    _r("T2", 2, [("trend", "is", "worse"), ("age", "in", YOUNG + ["senior"])],
       "Symptoms that are getting worse in a baby, child or older adult should be checked soon."),
    _r("T3", 2, [("trend", "is", "worse"), ("risk", "is", "yes")],
       "Symptoms that are getting worse with a long-term illness, a weakened immune system or pregnancy should be checked soon."),
    _r("M1", 2, [("medicine", "is", "nohelp")],
       "A fever or headache that does not respond to medicine should be checked soon."),

    # ── Not covered ────────────────────────────────────────────────────────
    _r("X1", 2, [("complaint", "is", "other")],
       "This checker only covers fever, cough, sore throat, headache and stomach upset. For anything else, talk to a doctor or nurse."),
]

# ---------------------------------------------------------------------------
# Advice shown with the result
# ---------------------------------------------------------------------------

ADVICE = {
    4: [
        "Call your local emergency number now (for example 911, 999 or 112).",
        "Do not drive yourself. Stay with the person and unlock the door if you can.",
        "Follow the instructions of the call-taker, and do not eat or drink unless told to.",
    ],
    3: [
        "Get medical care today: a same-day appointment, an urgent-care clinic, or your local nurse or health advice line.",
        "If it gets worse, or you cannot be seen soon, go to emergency care.",
        "Take a list of medicines and, if you can, someone to go with you.",
    ],
    2: [
        "Book an appointment with a doctor or clinic within 1 to 3 days.",
        "Meanwhile rest, drink fluids, and note how symptoms change.",
        "If any warning sign below appears, get care sooner.",
    ],
}

SELFHARM_ADVICE = (
    "If you or someone else may be in danger of self-harm, call your local emergency number. "
    "In the US you can also call or text 988 for crisis support; elsewhere, contact your local crisis line."
)

SELF_CARE = {
    "fever": [
        "Rest and drink plenty of fluids.",
        "Wear light clothing and keep the room comfortable, not cold.",
        "Paracetamol (acetaminophen) or ibuprofen can ease discomfort. Follow the label for the person's age, and never give aspirin to anyone under 16.",
    ],
    "cough": [
        "Rest and drink warm fluids. Honey in a warm drink can soothe a cough (not for babies under 1).",
        "Keep away from smoke.",
        "Most coughs from colds fade within about 3 weeks.",
    ],
    "throat": [
        "Drink warm fluids and rest your voice.",
        "Adults can gargle warm salt water or use throat lozenges (not for young children).",
        "Pain relief can help: follow the label for the person's age.",
    ],
    "headache": [
        "Rest in a quiet, dim room and drink water.",
        "Eat regular meals, and try to keep a regular sleep pattern.",
        "Pain relief can help: follow the label, and avoid using it on most days of the week.",
    ],
    "stomach": [
        "Sip fluids little and often. An oral rehydration solution is best if you have one.",
        "Eat small, plain meals once you feel hungry.",
        "Rest and wash your hands often to avoid passing it on.",
    ],
}

WATCH_FOR = {
    "fever": [
        "A temperature of 40 °C (104 °F) or higher",
        "Fever lasting more than 3 days",
        "A stiff neck, a rash that does not fade, or being very drowsy",
        "Trouble breathing, or not keeping fluids down",
    ],
    "cough": [
        "Breathlessness at rest, or blue lips",
        "Coughing up blood",
        "A cough lasting more than 3 weeks",
        "Chest pain or a high fever",
    ],
    "throat": [
        "Not being able to swallow saliva, or drooling",
        "A muffled voice or being unable to open your mouth",
        "A high fever, or white patches on the tonsils",
        "Symptoms lasting more than a week",
    ],
    "headache": [
        "A sudden, severe headache unlike any before",
        "Fever with a stiff neck",
        "Vision changes, weakness, or repeated vomiting",
        "Pain that keeps getting worse",
    ],
    "stomach": [
        "Vomiting blood, or black or bloody stools",
        "Severe or worsening belly pain, or a hard belly",
        "Signs of dehydration, or not keeping fluids down",
        "Symptoms lasting more than a week",
    ],
}
