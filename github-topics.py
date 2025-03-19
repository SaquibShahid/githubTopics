import streamlit as st
import requests
from dotenv import load_dotenv
import os
from google import genai
import json
import re

load_dotenv()
GITHUB_API_KEY = os.environ.get("GITHUB_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# def format_topic(topic_key: str) -> str:
#     parts = topic_key.split('-')
#     formatted = "+".join(f"topic:{part}" for part in parts)
#     return formatted

# def generate_github_query(json_response):
#     try:
#         data = json.loads(json_response)
#         keywords = data.get("keywords", "")

#         query_string = "+".join(keywords.replace(",", "").replace(" ","").split())

#         return query_string
#     except json.JSONDecodeError:
#         return ""


def generate_github_query(json_response):
    try:
        if not json_response:  # Handle empty responses
            print("Error: json_response is empty or None.")
            return ""

        json_response = clean_json_string(json_response)  # Clean unwanted formatting
        print(f"Cleaned JSON: {repr(json_response)}")  # Debugging

        data = json.loads(json_response)  # Convert JSON string to dictionary

        keywords = data.get("keywords", "")

        # Ensure proper handling of spaces and commas
        keyword_list = [word.strip().replace(" ","") for word in keywords.split(",")]

        # Convert to GitHub API format: topic:keyword+topic:keyword
        query_string = "+".join(f"{word}" for word in keyword_list)

        return query_string
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return ""

def clean_json_string(json_response):
    """Remove Markdown-style triple backticks from JSON strings"""
    json_response = json_response.strip()
    json_response = re.sub(r"^```json\n|\n```$", "", json_response)  # Remove ```json and ```
    return json_response

def generate_github_query_for_topic(json_response):
    try:
        if not json_response:  # Handle empty responses
            print("Error: json_response is empty or None.")
            return ""

        json_response = clean_json_string(json_response)  # Clean unwanted formatting
        print(f"Cleaned JSON: {repr(json_response)}")  # Debugging

        data = json.loads(json_response)  # Convert JSON string to dictionary

        keywords = data.get("keywords", "")

        # Ensure proper handling of spaces and commas
        keyword_list = [word.strip().replace(" ","") for word in keywords.split(",")]

        # Convert to GitHub API format: topic:keyword+topic:keyword
        query_string = "+".join(f"topic:{word}" for word in keyword_list)

        return query_string
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return ""

# def format_description(topic_key: str) -> str:
#     parts = topic_key.split('-')
#     formatted = "+".join(f"{part}" for part in parts)
#     return formatted

def fetch_repos_by_topic(topic):
        headers = {
            'Accept': 'application/vnd.github.mercy-preview+json'  # Needed for topic preview
        }
        headers['Authorization'] = f'token {GITHUB_API_KEY}'

        topic = generate_github_query_for_topic(topic)
        print("Fetching" , topic)
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

def fetch_repos_by_description(topic):
        headers = {
            'Accept': 'application/vnd.github.mercy-preview+json'  # Needed for topic preview
        }
        headers['Authorization'] = f'token {GITHUB_API_KEY}'

        topic = generate_github_query(topic)
        
        url = f"https://api.github.com/search/repositories?q={topic}&sort=stars&order=desc"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise exception for HTTP errors
            repos = response.json()['items']

            if not repos:
                print(f"No repositories found with description '{topic}'")
                return []

            return repos
                
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            return []

def get_topic_name(prompt):
    client = genai.Client(api_key=GEMINI_API_KEY)
    try:
        response = client.models.generate_content(
        model=f"gemini-2.0-flash", contents=f"Extract all the relevant technical keywords from the following user prompt. Focus on programming languages, frameworks, libraries, and specific domain terms that would be useful for searching GitHub repositories. Return the result as a JSON object with a key called ‘keywords’ that contains a comma-separated list of the extracted terms.User Prompt: '{prompt}'"
        )
        # model=f"gemini-2.0-flash", contents=f"generate key words from the given sentence and join them using '-' , sentence : {prompt}"
        # )
        # topic = response.text.replace("*", "").replace("#", "").replace(" ", "-")
        return response.text
    except Exception as e:
        print("Error generating data:", e)
        return ""


st.title("Github Treasure Hunter")


prompt = st.text_input("Enter the topic for what you need a Github repository :")
if prompt:
    topic = get_topic_name(prompt)
    if not topic:
        print(f"Error making API request")
    else:
        repos = fetch_repos_by_topic(topic)
        reposByDesc = fetch_repos_by_description(topic)
        if len(repos) <= 0 and len(reposByDesc) <= 0:
            print(f"Repositories not found")
            st.markdown(f"**Repositories not found**")
        else:
            repos.extend(reposByDesc)
            cols = st.columns(1)
            for idx, topic in enumerate(repos[:9]):
                with cols[idx%1]:
                    if topic['description'] is not None:
                        length = len(topic['description'])
                    else:
                        length = 0
                    st.markdown(f"Name : **{topic['name']}**")
                    st.markdown(f"Description : **{ topic['description'][:250] + "..." if length > 250 else topic['description']}**")
                    st.markdown(f"Stars : **{topic['stargazers_count']}**")
                    st.markdown(f"Tags : **{', '.join(topic['topics'])}**")
                    st.markdown(f"Link : **{topic['html_url']}**")
                    st.markdown("\n" + "="*88 + "\n")