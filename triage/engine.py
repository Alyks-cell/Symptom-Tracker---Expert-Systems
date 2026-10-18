"""Inference engine: forward chaining, conflict resolution, question control, explanations."""

from .knowledge import (
    ADVICE, DISCLAIMER, LEVELS, QUESTION_BY_ID, QUESTIONS, RULES,
    SELFHARM_ADVICE, SELF_CARE, WATCH_FOR,
)


# ---------------------------------------------------------------------------
# Inference engine
# ---------------------------------------------------------------------------


def label_of(qid, value):
    for option in QUESTION_BY_ID[qid]["options"]:
        if option["value"] == value:
            return option["label"]
    return str(value)


def match(condition, facts):
    """True if a single condition holds. Unanswered facts never match."""
    fact, op, value = condition
    answer = facts.get(fact)
    if answer is None:
        return False
    if op == "is":
        return answer == value
    if op == "in":
        return answer in value
    if op == "has":
        return isinstance(answer, list) and any(v in answer for v in value)
    if op == "lacks":
        return isinstance(answer, list) and not any(v in answer for v in value)
    raise ValueError(f"unknown operator {op}")


def fire_rules(facts):
    """Forward chaining: every rule whose conditions all hold fires."""
    return [rule for rule in RULES if all(match(c, facts) for c in rule["if"])]


def describe_condition(condition):
    fact, op, value = condition
    short = QUESTION_BY_ID[fact]["short"]
    names = [label_of(fact, v) for v in (value if isinstance(value, list) else [value])]
    if op == "is":
        return f"{short} is “{names[0]}”"
    if op == "in":
        return f"{short} is one of: " + "; ".join(f"“{n}”" for n in names)
    if op == "has":
        return f"{short} includes: " + "; ".join(f"“{n}”" for n in names) + " (any)"
    return f"{short} includes none of: " + "; ".join(f"“{n}”" for n in names)


def describe_rule(rule):
    return {
        "id": rule["id"],
        "level": rule["level"],
        "level_label": LEVELS[rule["level"]]["label"],
        "if": [describe_condition(c) for c in rule["if"]],
        "then": rule["reason"],
    }


def rules_using(qid):
    return sorted({r["id"] for r in RULES for c in r["if"] if c[0] == qid})


def applies(question, facts):
    """A question is asked only when all of its conditions hold."""
    return all(match(c, facts) for c in question["when"])


def unanswered(facts):
    return [q for q in QUESTIONS if q["id"] not in facts and applies(q, facts)]


def validate_facts(raw):
    """Check untrusted answers against the question definitions."""
    if not isinstance(raw, dict):
        raise ValueError("facts must be an object")
    facts = {}
    for qid, answer in raw.items():
        question = QUESTION_BY_ID.get(qid)
        if question is None:
            raise ValueError(f"unknown question: {qid}")
        values = {o["value"] for o in question["options"]}
        if question["type"] == "single":
            if not isinstance(answer, str) or answer not in values:
                raise ValueError(f"invalid answer for {qid}")
            facts[qid] = answer
        else:
            if (not isinstance(answer, list) or not answer or len(answer) > len(values)
                    or not all(isinstance(a, str) and a in values for a in answer)
                    or len(set(answer)) != len(answer)):
                raise ValueError(f"invalid answer for {qid}")
            if "none" in answer and len(answer) > 1:
                raise ValueError(f"'none' cannot be combined for {qid}")
            facts[qid] = list(answer)
    return facts


def build_result(facts, fired):
    top = max((r["level"] for r in fired), default=2)
    level = LEVELS[top]
    top_rules = sorted((r for r in fired if r["level"] == top), key=lambda r: r["id"])
    others = sorted((r for r in fired if r["level"] < top and r["level"] > 1), key=lambda r: (-r["level"], r["id"]))
    complaint = facts.get("complaint")

    if top == 1:
        advice = list(SELF_CARE.get(complaint, []))
    else:
        advice = list(ADVICE[top])
    if "selfharm" in facts.get("redflags", []):
        advice.insert(0, SELFHARM_ADVICE)

    answers = []
    for q in QUESTIONS:
        if q["id"] in facts:
            answer = facts[q["id"]]
            values = answer if isinstance(answer, list) else [answer]
            answers.append({"question": q["short"], "answer": "; ".join(label_of(q["id"], v) for v in values)})

    return {
        "level": top,
        "key": level["key"],
        "label": level["label"],
        "action": level["action"],
        "reasons": [describe_rule(r) for r in top_rules],
        "also_noted": [describe_rule(r) for r in others],
        "advice": advice,
        "watch_for": WATCH_FOR.get(complaint, []) if top <= 2 else [],
        "trace": [describe_rule(r) for r in sorted(fired, key=lambda r: (-r["level"], r["id"]))],
        "answers": answers,
        "questions_asked": len(facts),
        "resolution": (
            "Several rules can fire at once. The highest urgency among them decides the result, "
            "so a danger sign is never outvoted by milder findings."
        ),
        "disclaimer": DISCLAIMER,
    }


def next_step(raw_facts):
    """One turn of the consultation: the next question, or the final result."""
    facts = validate_facts(raw_facts)
    fired = fire_rules(facts)
    # Stop early on an emergency: asking more questions would only delay help.
    if any(r["level"] == 4 for r in fired):
        return {"done": True, "result": build_result(facts, fired)}
    pending = unanswered(facts)
    if not pending:
        return {"done": True, "result": build_result(facts, fired)}

    question = pending[0]
    return {
        "done": False,
        "question": {
            "id": question["id"],
            "text": question["text"],
            "type": question["type"],
            "options": question["options"],
            "why": question["why"],
            "used_by": rules_using(question["id"]),
        },
        "progress": {"answered": len(facts), "total": len(facts) + len(pending)},
    }


def handle_triage(data):
    """Shared by the local server and the Vercel function: (status, payload)."""
    try:
        return 200, next_step(data.get("facts", {}))
    except ValueError as err:
        return 400, str(err)
