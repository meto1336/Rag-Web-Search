from groq import Groq
import streamlit as st
import os
from dotenv import load_dotenv
import requests
import json
from bs4 import BeautifulSoup

# Set the Streamlit page configuration
st.set_page_config(page_title="RAG for Web Search", page_icon="🔍", initial_sidebar_state="collapsed")

# Load environment variables from a .env file
load_dotenv()

# Initialize the Groq client with the API key from environment variables
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Set the title of the Streamlit app
st.title("RAG for Web Search")

# Get the search query from the user input
query = st.text_input("Enter your search query:")
if query == "":
    st.stop()  # Stop execution if the query is empty

# Construct the search URL with the user's query
link = f"https://searx.be/search?q={query}&region=de&engines=bing"

# Define the headers for the HTTP request
header = {
    "accept-language": "de-DE,de;q=0.9,en;q=0.8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.36",
}

# Send the HTTP request to the search URL
r = requests.get(link, headers=header)

# Get the HTML content from the response
html_content = r.text

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Initialize an empty list to store the structured output
structured_output = []

# Find all snippets and URLs in the parsed HTML
snippets = soup.findAll("p", {"class": "content"})
urls = soup.findAll("a", {"class": "url_header"})

# Loop through the snippets and URLs and add them to the structured output
for snippet, url in zip(snippets, urls):
    structured_output.append({"Snippet": snippet.text, "Source": url["href"]})

# Format the structured output as a JSON string
output_formatted = json.dumps(structured_output, indent=4)

# Load the formatted JSON string into a list
output_list = json.loads(output_formatted)

# Define the system prompt for the LLM
system_prompt = f"Generate a detailed and concise response with a maximum of 300 words using only the provided structured snippets: {output_formatted}. If the user's query is a question, provide a direct answer in the first paragraph based on the structured snippets. Then, expand with relevant details using clear, well-structured paragraphs with headings and appropriate spacing. Do not include any commentary, introduction, or conclusion. The response should be in the same language as the user's query. If there are conflicting pieces of information, identify the discrepancies and either clarify them or provide the most accurate and coherent response possible. Ensure there are no contradictions in the response."

# Define the LLM model to use
llm_model = "llama-3.3-70b-versatile"

# Generate the chat completion using the Groq client
chat_completion = client.chat.completions.create(
    messages=[
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": query,
        },
    ],
    model=llm_model,
)

# Get the response from the LLM
llm_response = chat_completion.choices[0].message.content

# Display the LLM response in the Streamlit app
st.markdown(llm_response)

# Display the structured output in the sidebar
for item in output_list:
    st.sidebar.markdown(f"**Snippet**: {item['Snippet']}  \n\n**Source**: {item['Source']}")

