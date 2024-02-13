import json
import os
import time

import github
import requests

import auth
from github import Auth, Github
from openai import OpenAI

import prompts

import re

INLINE_LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
FOOTNOTE_LINK_TEXT_RE = re.compile(r'\[([^\]]+)\]\[(\d+)\]')
FOOTNOTE_LINK_URL_RE = re.compile(r'\[(\d+)\]:\s+(\S+)')
SESSION = time.time()


# Ensure directories exist
def ensure_dir_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


# Save content to a file
def save_content(file_path, content):
    if file_path[-5:] == ".json":
        with open(file_path, 'w', encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
    else:
        with open(file_path, 'w', encoding="utf-8") as f:
            f.write(content)


# Find and process articles from a specific GitHub repository
def find_articles(github_client, chatgpt_client):
    repo = github_client.get_repo("MicrosoftDocs/dynamics-365-unified-operations-public")
    contents = repo.get_contents("articles/fin-ops-core/fin-ops/get-started")

    for content_file in contents:
        path = content_file.path
        file_name = path.replace("articles/fin-ops-core/fin-ops/get-started/", "")
        if "whats-new-platform-updates" in file_name:

            file_name = file_name.replace(".md", "")
            base_path = f"./Articles/{SESSION}/{file_name}"

            ensure_dir_exists(f"{base_path}/transcript")
            print(SESSION, "DIRECTORY INITIATED")

            # Fetch Update Notes Article
            article = repo.get_contents(path).decoded_content

            # Fetch Links From Article
            links = find_md_links(str(article))
            citations = {}
            for link in links:
                label = link[0]  # Label
                link = link[1]  # Link/Path
                if link[0] in ["/", "."]:  # Ignore Absolute
                    try:
                        content = str(repo.get_contents("articles/fin-ops-core/fin-ops/get-started/" + link).decoded_content)
                        if len(content.strip()) > 500:  # Anything less than 500 characters is probably not important
                            content = summarise_article_chain(chatgpt_client, "UnderstandReference", content)
                            citations[link] = {"label": label, "content": content}
                    except Exception as e:
                        pass

            references_file_path = f"{base_path}/references.json"
            save_content(references_file_path, citations)

            # article_content = summarise_article(chatgpt_client, article)
            article_content = summarise_article_chain(chatgpt_client, "ExtractKeyPoints", article)

            # Here we improve the generated article by questioning if any points can be elaborated using the citations.
            article_content_improved = summarise_article_chain(chatgpt_client, "ReinforceReferences", article_content + json.dumps(citations))

            thumbnail_url = ""
            transcript = ""

            # From Summary Generate Thumbnail
            # thumbnail_url = generate_thumbnail(chatgpt_client, file_name, article_content)

            # From Summary Generate Audio Transcript
            #transcript = summarise_article_audio(chatgpt_client, article_content)

            article_file_path = f"{base_path}/{file_name}.md"
            transcript_file_path = f"{base_path}/transcript/{file_name}.md"

            save_article(article_file_path, article_content, article_content_improved, thumbnail_url, content_file)
            save_content(transcript_file_path, transcript)

            # Generate Audio From Transcript
            # generate_audio(chatgpt_client, file_name, transcript)

            break  # Remove if you want to process more than one article


def find_md_links(md):
    """ Return dict of links in markdown """

    links = list(INLINE_LINK_RE.findall(md))
    footnote_links = dict(FOOTNOTE_LINK_TEXT_RE.findall(md))
    footnote_urls = dict(FOOTNOTE_LINK_URL_RE.findall(md))

    for key in footnote_links.keys():
        links.append((footnote_links[key], footnote_urls[footnote_links[key]]))

    return links


# Save article content along with thumbnail and link
def save_article(file_path, article_content, article_content_improved, thumbnail_url, original_article_link):

    # Original Article summary
    content = f"{article_content}\n\n![Thumbnail]({thumbnail_url})\n[Full Article]({original_article_link})"
    save_content(file_path[:-3] + "-original.md", content)

    # Revised Article
    content = f"{article_content_improved}\n\n![Thumbnail]({thumbnail_url})\n[Full Article]({original_article_link})"
    save_content(file_path, content)


# Summarize the article using ChatGPT
def summarise_article(chatgpt_client, article):
    prompt = prompts.article_prompts["GPT4Generated"] + "The following is the content you should use for this task." + str(article)
    response = chatgpt_client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="gpt-3.5-turbo")
    return response.choices[0].message.content


def summarise_article_chain(chatgpt_client, chainKey, article): #str(article)
    messages = [{"role": "system", "content": "Here are software release notes: " + str(article)}] + prompts.chains[chainKey]
    response = chatgpt_client.chat.completions.create(messages=messages, model="gpt-3.5-turbo")
    return response.choices[0].message.content


# Generate a thumbnail for the article
def generate_thumbnail(chatgpt_client, file_name, article):
    prompt = "Extract keywords from this article and design an illustration around a physical object that relates to these keywords." + "Article:" + article
    response = chatgpt_client.images.generate(prompt=prompt, n=1, size="1024x1024", quality="hd", style="vivid")
    image_url = response.data[0].url
    img_data = requests.get(image_url).content
    with open(f"Articles/{file_name}/{file_name}.jpg", 'wb') as handler:
        handler.write(img_data)
    return image_url


# Summarize the article for audio transcript
def summarise_article_audio(chatgpt_client, article):
    prompt = "Create an audio transcript from this article suitable for the OpenAI speech API."
    response = chatgpt_client.chat.completions.create(messages=[{"role": "user", "content": prompt + str(article)}], model="gpt-3.5-turbo")
    return response.choices[0].message.content


# Generate audio from the transcript
def generate_audio(chatgpt_client, file_name, transcript):
    speech_file_path = "Articles/" + file_name + "/" + file_name + ".mp3"
    response = chatgpt_client.audio.speech.create(model="tts-1", voice="alloy", input=transcript)
    response.stream_to_file(speech_file_path)


# Authenticate with GitHub
def authenticate_git():
    key = auth._GHTAILOR
    github_client = Github(key)
    return github_client


# Authenticate with OpenAI
def authenticate_chatgpt():
    api_key = auth._OAITAILOR
    chatgpt_client = OpenAI(api_key=api_key)
    return chatgpt_client


if __name__ == '__main__':
    github_client = authenticate_git()
    chatgpt_client = authenticate_chatgpt()
    find_articles(github_client, chatgpt_client)