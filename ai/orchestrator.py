from ai.intent_model import create_session, recognize_intent
from ai.validator import validator



FIELD_QUESTIONS = {
    "name": "What product are you referring to?",
    "quantity": "How many units?",
    "selling_price": "What is the selling price?",
    "cost_price": "What is the cost price?",
}

def process_message(message: str, session: dict) -> dict:
    """
    Full pipeline:
    1. Send message + session to LLM
    2. If LLM returns final → validate
       - If valid → ready to call API
       - If invalid → send errors back to LLM for user-friendly follow-up
    3. If LLM returns clarification → pass message to user
    4. Update session state throughout
    """

    llm_result = recognize_intent(message, session)

    response_type = llm_result.get("type")

    # ── LLM couldn't understand ──────────────────────────────────────────────
    if response_type == "unknown" or response_type == "error":
        return {
            "status": "unknown",
            "message": llm_result.get("message", "I didn't understand that.")
        }

    # ── LLM is asking the user for more info ─────────────────────────────────
    if response_type == "clarification":
        # Persist whatever partial data the LLM already extracted
        session["intent"] = llm_result.get("intent")
        session["class"] = llm_result.get("class")
        session["data"].update(llm_result.get("data", {}))

        return {
            "status": "clarification",
            "message": llm_result.get("message"),
            "missing_fields": llm_result.get("missing_fields", [])
        }

    # ── LLM thinks it has everything — validate ───────────────────────────────
    if response_type == "final":
        msg_class = llm_result.get("class")
        intent    = llm_result.get("intent")
        data      = llm_result.get("data", {})

        # Merge with session data so follow-up answers fill earlier gaps
        merged_data = {**session.get("data", {}), **data}

        validation = validator(msg_class, intent, merged_data)

        if validation["valid"]:
            # Update session with confirmed data
            session["intent"] = intent
            session["class"]  = msg_class
            session["data"]   = merged_data

            return {
                "action": "call_api",
                "status": "ready",
                "class":  msg_class,
                "intent": intent,
                "data":   merged_data
            }

        else:
            # Feed validation errors back to LLM so it asks the user naturally
            error_feedback = _build_error_feedback(intent, validation["errors"])
            follow_up      = recognize_intent(error_feedback, session)

            # Store partial data anyway
            session["intent"] = intent
            session["class"]  = msg_class
            session["data"].update(merged_data)

            return {
                "status": "clarification",
                "message": follow_up.get(
                    "message",
                    "Some information is missing, could you clarify?"
                ),
                "missing_fields": [e["field"] for e in validation["errors"]]
            }

    return {"status": "unknown", "message": "Unexpected response from model."}


def _build_error_feedback(intent: str, errors: list) -> str:
    """
    Formats validator errors into a prompt the LLM uses
    to ask the user for the missing/invalid fields.
    """
    lines = [
        f"The user is trying to: {intent}.",
        "The following fields are missing or invalid:"
    ]
    for err in errors:
        field   = err.get("field", "unknown")
        message = err.get("message", "invalid value")
        lines.append(f"  - {field}: {message}")

    lines.append(
        "Ask the user a single, natural question to collect this information."
    )
    return "\n".join(lines)


# FIX 1 & 2: __main__ now passes a session and reads result keys safely
if __name__ == "__main__":
    print("Retail AI Assistant (type 'exit' to quit)")
    print("=" * 70)

    session = create_session()

    while True:
        message = input("\nYou: ").strip()

        if message.lower() in ["exit", "quit"]:
            print("Exiting...")
            break

        result = process_message(message, session)

        # 🧠 Handle system responses
        if result.get("action") == "call_api":
            print("\n✅ FINAL OUTPUT (Ready for API)")
            print(f"Intent: {result['intent']}")
            print(f"Class: {result['class']}")
            print(f"Data: {result['data']}")

            # Reset session after completion
            # session = create_session()

        elif result.get("reply"):
            print(f"\nAI: {result['reply']}")

        else:
            print("\n⚠️ Unexpected response:", result)