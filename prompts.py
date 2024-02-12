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
    "ExtractKeyPoints": [
        {"role": "user", "content": "Extract new features from the software update notes."},
        {"role": "user", "content": "Extract changed features from the software update notes."},
        {"role": "user", "content": "Extract important features from the software update notes."},
        {"role": "user", "content": "Extract availability dates from the software update notes."},
        {"role": "user", "content": "Write an unbiased and unexaggerated linked in post mentioning these new features, changed features, important features and availability from these software update notes, be educational."},
        {"role": "system", "content": "Review your linked in post. If it is missing any key points, add them. If it's inconsisent with the original software update notes, fix it. "},
        {"role": "system", "content": "You're a Finance & Operations user. Review this document and re-write it to align more with your user viewpoint"}
    ]
}