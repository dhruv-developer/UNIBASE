# unibase/utils/groq_integration.py

import os
try:
    from groq import Groq
except ImportError:
    class Groq:
        def __init__(self, api_key):
            self.api_key = api_key

        class chat:
            @staticmethod
            def completions_create(messages, model):
                class Choice:
                    message = type("Message", (), {"content": "Dummy AI insight based on the query."})
                class Response:
                    choices = [Choice()]
                return Response()
    print("groq module not found, using dummy Groq client.")

def get_insights(query_text):
    api_key = "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"
    client = Groq(api_key=api_key)
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": query_text}],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content
