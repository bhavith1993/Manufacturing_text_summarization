import json
import os
import boto3

BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-west-2")
MODEL_ID = os.getenv("MODEL_ID", "cohere.command-r-v1:0")

client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

def _resp(status_code: int, body: dict):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }

def _parse_payload(event):
    # Supports:
    # - API Gateway proxy: event["body"] is JSON string
    # - Direct invoke: event is already a dict
    if not isinstance(event, dict):
        return {}, "Invalid event type"

    if "body" in event and isinstance(event["body"], str):
        try:
            return json.loads(event["body"]), None
        except json.JSONDecodeError:
            return {}, "Invalid JSON in request body"

    return event, None

def lambda_handler(event, context):
    payload, err = _parse_payload(event)
    if err:
        return _resp(400, {"error": err})

    # Accept either a raw prompt OR structured manufacturing inputs
    prompt = (payload.get("prompt") or "").strip()

    # Optional structured fields (makes it look like a real manufacturing assistant)
    task = (payload.get("task") or "").strip()              # e.g., "SOP", "5-Why", "CAPA", "Handover"
    process = (payload.get("process") or "").strip()        # e.g., "CNC milling"
    issue = (payload.get("issue") or "").strip()            # e.g., "surface finish defects"
    constraints = (payload.get("constraints") or "").strip()# e.g., "ISO 9001, keep it short"
    audience = (payload.get("audience") or "operators").strip()
    tone = (payload.get("tone") or "clear, practical").strip()

    if not prompt:
        # Build a prompt from structured fields if prompt not provided
        if not (task and (process or issue)):
            return _resp(400, {
                "error": "Provide either 'prompt' OR ('task' and one of 'process'/'issue')."
            })
        prompt = f"""
You are a manufacturing operations assistant.
Task: {task}
Audience: {audience}
Tone: {tone}
Process: {process or "N/A"}
Issue: {issue or "N/A"}
Constraints: {constraints or "N/A"}

Write the best response. Use bullet points where useful. Be specific and actionable.
""".strip()

    # Bedrock-native request for Command R/R+ uses "message" (+ optional "chat_history") :contentReference[oaicite:1]{index=1}
    native_request = {
        "message": prompt,
        "max_tokens": int(payload.get("max_tokens", 600)),
        "temperature": float(payload.get("temperature", 0.4)),
        "p": float(payload.get("p", 0.9)),
        "k": int(payload.get("k", 0)),
    }

    # Optional chat history (array of {"role":"USER|CHATBOT","message":"..."}) :contentReference[oaicite:2]{index=2}
    chat_history = payload.get("chat_history")
    if isinstance(chat_history, list):
        native_request["chat_history"] = chat_history

    try:
        resp = client.invoke_model(
            modelId=MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(native_request),
        )
        data = json.loads(resp["body"].read())
    except Exception:
        return _resp(502, {"error": "Bedrock invoke failed"})

    # Command R examples show the generated text in "text" :contentReference[oaicite:3]{index=3}
    answer = data.get("text")
    if not isinstance(answer, str):
        return _resp(502, {"error": "Unexpected model response format", "raw": data})

    return _resp(200, {"response": answer, "modelId": MODEL_ID})
