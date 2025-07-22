from flask import Flask, request, jsonify
import openai
import time
import os

app = Flask(__name__)

openai.api_key = os.getenv("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")
ASSISTANT_ID = os.getenv("asst_deIP0iaZjQpt4uSaWDjiiOLa")

@app.route("/search", methods=["POST"])
def search():
    try:
        query = request.json.get("query", "")

        thread = openai.beta.threads.create()

        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )

        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        while True:
            status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if status.status == "completed":
                break
            elif status.status in ["failed", "cancelled"]:
                return jsonify({"answer": "Асистент не зміг виконати запит."}), 500
            time.sleep(1)

        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        latest = messages.data[0].content[0].text.value

        return jsonify({"answer": latest})
    
    except Exception as e:
        print("Помилка:", e)
        return jsonify({"answer": "Внутрішня помилка сервера.", "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
