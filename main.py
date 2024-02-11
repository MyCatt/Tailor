import github
from github import Auth, Github
from openai import OpenAI


def find_articles():
    repo = g.get_repo("MicrosoftDocs/dynamics-365-unified-operations-public")
    contents = repo.get_contents("articles/fin-ops-core/fin-ops/get-started")

    for content_file in contents:
        path = content_file.path
        file_name = path.replace("articles/fin-ops-core/fin-ops/get-started/", "")
        if "whats-new-platform-updates" in file_name:
            article = repo.get_contents(path)
            article_content = summarise_article(article)
            thumbnail_prompt = create_thumbnail(article_content)
            thumbnail = generated_thumbnail(thumbnail_prompt)
            save_article(file_name, article_content, thumbnail)
            return

    # To close connections after use
    g.close()


def save_article(file_name, article_content, thumbnail):
    with open("Articles/" + file_name, 'w', encoding="utf-8") as f:
        f.write(article_content)
        f.write("\n\n![Thumbnail](" +thumbnail + ")")
        f.write('\n[Full Article] ' + "https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/fin-ops/get-started/" + file_name)


def summarise_article(article):
    chat_completion = c.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Write an honest and engaging Linked In post summarising the following update release notes. The readers of this are less technical users that want to stay up to date. "
                           "You do not work for this company, you're just creating an easier way of reading it."
                           "This article should have a corporate style"
                            "Write a catchy relevant title"
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


def generated_thumbnail(context):
    image_completion = c.images.generate(
        model="dall-e-3",
        prompt= context + ". Characteristics: Mandatory colors: [#7F27FF, #FF8911], gradient, dimensional graphic design, Illusion of live-like depth and volume, Employs various lighting effects, Shadow and depth indications often utilise one colour, with tonal variations",
        n=1,
        size="1024x1024",
        quality="hd",
        style="vivid"
    )
    image_url = image_completion.data[0].url
    return image_url



def authenticate_git():
    # using an access token
    auth = Auth.Token("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")

    # First create a Github instance:

    # Public Web Github
    g = Github(auth=auth)
    return g


def authenticate_chatgpt():
    client = OpenAI(api_key="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")
    return client

if __name__ == '__main__':
    g = authenticate_git()
    c = authenticate_chatgpt()
    find_articles()
