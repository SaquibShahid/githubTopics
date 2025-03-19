import streamlit as st
import requests
from dotenv import load_dotenv
import os
from google import genai

load_dotenv()
GITHUB_API_KEY = os.environ.get("GITHUB_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def format_topic(topic_key: str) -> str:
    parts = topic_key.split('-')
    formatted = "+".join(f"topic:{part}" for part in parts)
    return formatted

def fetch_repos_by_topic(topic):
        headers = {
            'Accept': 'application/vnd.github.mercy-preview+json'  # Needed for topic preview
        }
        headers['Authorization'] = f'token {GITHUB_API_KEY}'

        topic = format_topic(topic)
        
        url = f"https://api.github.com/search/repositories?q={topic}&sort=stars&order=desc"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise exception for HTTP errors
            repos = response.json()['items']

            if not repos:
                print(f"No repositories found with topic '{topic}'")
                return []

            return repos
                
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            return []

def get_topic_name(prompt):
    client = genai.Client(api_key=GEMINI_API_KEY)
    try:
        response = client.models.generate_content(
        model=f"gemini-2.0-flash", contents=f"generate key words from the given sentence and join them using '-' , sentence : {prompt}"
        )
        print(response.text)
        topic = response.text.replace("*", "").replace("#", "").replace(" ", "-")
        return topic
    except Exception as e:
        print("Error generating data:", e)
        return ""


st.title("Github Treasure Hunter")

prompt = st.text_input("Enter the topic for what you need a Github repository :")
if prompt:
    topic = get_topic_name(prompt)
    if topic == "":
        print(f"Error making API request")
    else:
        repos = fetch_repos_by_topic(topic)
        if len(repos) <= 0:
            print(f"Repositories not found")
            st.markdown(f"**Repositories not found**")
        else:
            cols = st.columns(1)
            for idx, topic in enumerate(repos[:9]):
                with cols[idx%1]:
                    st.markdown(f"Name : **{topic['name']}**")
                    st.markdown(f"Description : **{topic['description']}**")
                    st.markdown(f"Stars : **{topic['stargazers_count']}**")
                    st.markdown(f"Tags : **{', '.join(topic['topics'])}**")
                    st.markdown(f"Link : **{topic['html_url']}**")
                    st.markdown("\n" + "="*88 + "\n")