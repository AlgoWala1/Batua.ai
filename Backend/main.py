from fastapi import FastAPI
import json
import requests
import os
from prompts import TOOL_CHAINING, RESPONSE_PROMPT
from dotenv import load_dotenv

from tools import orchestrator
import data_handlers as dh
import logging as log

### Backend Chat api definition goes here
load_dotenv()
app = FastAPI()

@app.on_event("startup")
def status():
    # Load csv name to ticker content
    print("ChatAPI started")
    log.info("Initializing company names")
    dh.init_ticker_dict()
    return {'running': True, 'description': "Listening to requests"}

@app.get('/query')
def query(question: str):
    print("Received question:", question)
    try:
        response = invoke_llm(TOOL_CHAINING, question)

        def clean_resonse(response):
            data = response['choices'][0]['message']['content']
            data = data.replace("json", "")
            clean_data = data.replace("```", "").strip() 
            return clean_data
        
        clean_data = clean_resonse(response)
        actions = json.loads(clean_data)

        tool_response = orchestrator(actions['instruction'], actions['parameters'])
        modified_query = f"{question} \n\n 'json to answer from': {json.dumps(tool_response)}"
        print(json.dumps(tool_response))
        final_response = invoke_llm(RESPONSE_PROMPT, modified_query)
        # print("Final response from Groq API:", final_response)
        final_answer = clean_resonse(final_response)
        return {"answer": final_answer}
    except Exception as e:
        print(e)
    
def invoke_llm(prompt, query):
    url = f"https://api.groq.com/openai/v1/chat/completions"
    api_key = os.getenv("grok-api")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    instructions = {
        "model": os.getenv("model"),
        "messages": [
        {
        "role": "system",
        "content": prompt
        },
        {
        "role": "user",
        "content": query
        }
    ]
    }         
    response = requests.post(url, headers=headers, json=instructions).json()
    return response 