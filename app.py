from flask import Flask, request, jsonify
import os, time
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = os.environ.get("ASSISTANT_ID")  # впадемо вручну, якщо None

@app.post("/search")
def search():
    try:
        if not ASSISTANT_ID:
            return jsonify({"answer": "ASSISTANT_ID не задано у змінних оточення"}), 500

        body = request.get_json(force=True) or {}
        query = body.get("query", "").strip()
        if not query:
            return jsonify({"answer": "Порожній запит"}), 400

        thread = client.beta.threads.create()

        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # Полінг статусу
        while True:
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run.status == "completed":
                break
            if run.status in ("failed", "cancelled", "expired"):
                return jsonify({"answer": "Асистент не зміг виконати запит."}), 500
            time.sleep(1)

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        # шукаємо перше повідомлення від асистента
        latest_msg = next((m for m in messages.data if m.role == "assistant"), messages.data[0])
        latest = latest_msg.content[0].text.value

        return jsonify({"answer": latest})

    except Exception as e:
        print("Помилка:", e)
        return jsonify({"answer": "Внутрішня помилка сервера.", "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
