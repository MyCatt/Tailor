import os

import requests

import auth
from github import Auth, Github
from openai import OpenAI


def set_env_variable(gh, oai):
    os.environ['GHTAILOR'] = gh
    os.environ['OAITAILOR'] = oai


def find_articles():
    repo = g.get_repo("MicrosoftDocs/dynamics-365-unified-operations-public")
    contents = repo.get_contents("articles/fin-ops-core/fin-ops/get-started")

    for content_file in contents:
        path = content_file.path
        file_name = path.replace("articles/fin-ops-core/fin-ops/get-started/", "")
        if "whats-new-platform-updates" in file_name:

            os.mkdir("./Articles/" + file_name[:-3])
            os.mkdir("./Articles/" + file_name[:-3] + "/transcript")

            # Get the article content from git
            article = repo.get_contents(path)

            # Summarise the article with OpenAI
            article_content = summarise_article(article)

            # Generated a thumbnail using the article generated above
            thumbnail_prompt = create_thumbnail(article_content)
            # Generate a thumbnail using the prompt above
            thumbnail = generated_thumbnail(file_name[:-3], thumbnail_prompt)

            # Generate the audio transcript
            transcript = summarise_article_audio(article_content)

            # Save the article to a file
            save_article(file_name, article_content, thumbnail, transcript)

            # Generate and save the audio file
            generate_audio(file_name[:-3], transcript)

            return

    # To close connections after use
    g.close()


def save_article(file_name, article_content, thumbnail, transcript):
    with open("Articles/" + file_name[:-3] + "/" + file_name, 'w', encoding="utf-8") as f:
        f.write(article_content)
        f.write("\n\n![Thumbnail](" +thumbnail + ")")
        f.write('\n[Full Article] ' + "https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/fin-ops/get-started/" + file_name)

    with open("Articles/" + file_name[:-3] + "/transcript/" + file_name, 'w', encoding="utf-8") as f:
        f.write(transcript)


def summarise_article(article):
    chat_completion = c.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Write an honest and engaging Linked In post summarising the following update release notes."
                           "You do not work for this company, you're just creating an educational post."
                           "This article should have a strictly corporate style"
                           "The input (follows) and output are both markdown."
                           + str(article),
            }
        ],
        model="gpt-4-0125-preview",
    )
    print(chat_completion)
    content = chat_completion.choices[0].message.content
    print(content)
    return content


def summarise_article_audio(article):
    chat_completion = c.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "take this article and create an audio transcript that I can supply to the openAI speech API. This transcript should only include words that should be read and spoken directly."
                           + str(article),
            }
        ],
        model="gpt-4-0125-preview",
    )
    content = chat_completion.choices[0].message.content
    return content


def create_thumbnail(article):
    chat_completion = c.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Extract keywords from this article and design an illustration around a physical object that relates to these keywords.  e.g. Updates relates to Computer"
                           "Article:" + article
                           + str(article),
            }
        ],
        model="gpt-4-0125-preview",
    )
    content = chat_completion.choices[0].message.content
    return content


def generated_thumbnail(file_name, context):
    image_completion = c.images.generate(
        model="dall-e-3",
        prompt= context + ". Characteristics: Mandatory colors: [#7F27FF, #FF8911], gradient, dimensional graphic design, Illusion of live-like depth and volume, Employs various lighting effects, Shadow and depth indications often utilise one colour, with tonal variations",
        n=1,
        size="1024x1024",
        quality="hd",
        style="vivid"
    )
    image_url = image_completion.data[0].url
    img_data = requests.get(image_url).content
    with open("Articles/" + file_name + "/" + file_name +'.jpg', 'wb') as handler:
        handler.write(img_data)
    return image_url


def generate_audio(file_name, context):
    speech_file_path = "Articles/" + file_name + "/" + file_name + ".mp3"
    response = c.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=context
    )

    response.stream_to_file(speech_file_path)


def authenticate_git():
    # using an access token
    key = Auth.Token(auth._GHTAILOR)
    # First create a Github instance:
    # Public Web Github
    g = Github(auth=key)
    return g


def authenticate_chatgpt():
    client = OpenAI(api_key=auth._OAITAILOR)
    return client


if __name__ == '__main__':
    g = authenticate_git()
    c = authenticate_chatgpt()
    find_articles()
