import arxiv

client = arxiv.Client()

search = arxiv.Search(
    query="large language models",
    max_results=2
)

results = client.results(search)

for paper in results:
    print("TITLE:", paper.title)
    print("SUMMARY:", paper.summary[:300])
    print("--------------------")