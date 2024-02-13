article_prompts = {
    "MyFirstRevision": "Write an honest and engaging Linked In post summarising the following update release notes."
                       "You do not work for this company, you're just creating an educational post."
                       "This article should have a strictly corporate style"
                       "The input (follows) and output are both markdown.",
    "GPT4Generated": "Convert the following software update notes into a concise, engaging educational blog post "
                     "suitable for LinkedIn. "
                     "The post should introduce the key updates, "
                     "highlight the new features, "
                     "and discuss their benefits for users. Include practical tips on how "
                     "users can leverage these updates. "
                     "Aim for a professional yet conversational tone, and structure the post with an introduction, "
                     "key points, and a conclusion. "
}

chains = {
    "ExtractKeyPoints": [  # This prompt is used to extract and summarise the update notes.
        {"role": "user", "content": "Extract any new features from the software update notes."},
        {"role": "user", "content": "Extract any changed features from the software update notes."},
        {"role": "user", "content": "Extract any important features from the software update notes."},
        {"role": "user", "content": "Extract availability dates from the software update notes."},
        {"role": "user", "content": "Extract any information that you did not include in the previous prompts"},
        {"role": "user", "content": "Write an unbiased and unexaggerated article mentioning these new features, changed features, important features, additional information, and availability from these software update notes, be educational."},
        {"role": "system", "content": "Review your article. If it is missing any key points, add them. If it's inconsisent with the original software update notes, fix it. "}
        # {"role": "system", "content": "You're a Finance & Operations user. Review this document and re-write it to align more with your user viewpoint"}
    ],
    "ExtractKeyPoints2": [  # This prompt is used to extract and summarise the update notes.
        {"role": "user", "content": "Here are software update notes that I wrote, I want you to extract key features of this and put them into bullet points. I do not need descriptions, just labels for each. Do not create sub groups. The output should be bullet points only, with no additional data."},
        {"role": "user", "content": "Did your response extract all key features?"},
        {"role": "user", "content": "Send me a list of these bullet points, your response should only contain bullet points and no other text"},
        {"role": "user", "content": "Send me a list of these bullet points in JSON"}
    ],
    "UnderstandReference": [  # This prompt is used to gain information from links
        {"role": "user", "content": "Extract key takeaways from this document"},
        {"role": "user", "content": "Extract key points from this document"},
        {"role": "user", "content": "Extract important features from this document"},
        {"role": "user",
         "content": "Write an unbiased and unexaggerated summary mentioning these key takeaways, key points, and important features discovered in the last prompts, be educational."},
        {"role": "system",
         "content": "Review your summary. If it is missing any key points, add them. If it's inconsisent with the original document, fix it. "},
        #{"role": "system",
         # "content": "You're a Finance & Operations user. Review this document and re-write it to align more with your user viewpoint"}
    ],
    "ReinforceReferences": [  # This prompt is used to gain information from links
        {"role": "user", "content": "Provided is an article summarising software update notes, following that is a json object with further articles that might relate to the summarised software notes"},
        {"role": "user", "content": "Extract key points from this article and explain them using any relevant articles from the json object, cite these with a link if used and be descriptive"},
        {"role": "user",
         "content": "Write an unbiased and unexaggerated article mentioning these key takeaways, key points, and important features discovered in the last prompts - with links, be educational and informative."},
        {"role": "system",
         "content": "You're a Finance & Operations user. Review this document and re-write it to align more with your user viewpoint. If it's inconsisent with the original document, fix it. Remember to add availability dates (As bullet points), if included in the original article."},
        {"role": "system", "content": "Review your article. If it is missing any key points, add them. If it's inconsisent with the original software update notes, fix it. "}
    ]
}