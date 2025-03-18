import streamlit as st
import requests
from dotenv import load_dotenv
import os
from google import genai

load_dotenv()
GITHUB_API_KEY = os.environ.get("GITHUB_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def fetch_repos_by_topic(topic):
        headers = {
            'Accept': 'application/vnd.github.mercy-preview+json'  # Needed for topic preview
        }
        headers['Authorization'] = f'token {GITHUB_API_KEY}'
        
        url = f"https://api.github.com/search/repositories?q=topic:{topic}&sort=stars&order=desc"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise exception for HTTP errors
            repos = response.json()['items']

            if not repos:
                print(f"No repositories found with topic '{topic}'")
                return []
            
            # print(f"Found {len(repos)} repositories with topic '{topic}':\n")
            # for repo in repos:
            #     print(f"Name: {repo['name']}")
            #     print(f"Description: {repo['description']}")
            #     print(f"URL: {repo['html_url']}")
            #     print(f"Stars: {repo['stargazers_count']}")
            #     print(f"Topics: {', '.join(repo['topics'])}")
            #     print("\n" + "="*50 + "\n")

            return repos
                
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            return []

def get_topic_name(prompt):
    client = genai.Client(api_key=GEMINI_API_KEY)
    try:
        response = client.models.generate_content(
        model=f"gemini-2.0-flash", contents=f"make this sentence in one word tag that can be use to search in github , sentence : {prompt}"
        )
        topic = response.text.replace("*", "")
        print(topic)
        return topic
    except:
        print(f'Error generating data')
        return ""


st.title("AI GitHub Topic Expander")

prompt = st.text_input("Enter the topic for what you need a github repository :")
if prompt:
    topic = get_topic_name(prompt)
    if topic == "":
        print(f"Error making API request")
    else:
        repos = fetch_repos_by_topic(topic)
        print(repos)
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