from app.chunking.utils.tokens import (
    count_tokens,
    split_sentences,
)


text = """
Transformers changed NLP forever.

Large Language Models now solve reasoning tasks.

RAG improves factuality.
"""

print()

print(
    "Token Count:",
    count_tokens(text),
)

print()

print(
    "Sentences:",
)

for sentence in split_sentences(text):

    print(sentence)