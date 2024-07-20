from haystack.components.builders import PromptBuilder
from haystack.components.retrievers import InMemoryBM25Retriever
from haystack.core.pipeline import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.dataclasses import Document
from haystack_integrations.components.generators.ollama import OllamaGenerator
import json
from pprint import pprint
from pymongo import MongoClient


def safe_json_loads(json_string):
    try:
        return json.loads(json_string)
    except (TypeError, ValueError):
        return {}


def main():
    # I have a MongoDB replication Set, No User ID or Password..
    uri = "mongodb://mongo-1:27017,mongo-2:27117,mongo-3:27217/web-crawl"
    options = {
        'retryWrites': 'true',
        'w': 'majority',
        'loadBalanced': 'false',
        'serverSelectionTimeoutMS': '5000',
        'connectTimeoutMS': '10000',
        'replicaSet': 'rs0'
    }

    # Form the URI with options
    options_str = '&'.join([f"{key}={value}" for key, value in options.items()])
    uri_with_options = f"{uri}?{options_str}"

    # Initialize the MongoDocumentStore
    client = MongoClient(uri_with_options)
    db = client['web-crawl']
    collection = db['pages']

    template = """
    Given only the following information, answer the question.
    Ignore your own knowledge.

    Context:
    {% for document in documents %}
        {{ document.content }}
        Metadata:
        {% for key, value in document.meta.items() %}
            {{ key }}: {{ value }}
        {% endfor %}
    {% endfor %}

    Question: {{ query }}?
    """

    # Fetch documents from MongoDB. A Better solution is to
    # create a MongoDB Store, It looks like everything on
    # Haystack is a paid solution Such as Atlas.
    documents = [
        Document(
            id=doc['_id'],
            content=doc.get('content', ''),
            meta={
                'title': doc.get('title', ''),
                'url': doc.get('url', ''),
                'ldJsonScripts': [safe_json_loads(script) for script in doc.get('ldJsonScripts', [])],
                'imageUrls': doc.get('imageUrls', []),
                'pageHrefs': doc.get('pageHrefs', []),
                'linkTags': doc.get('linkTags', []),
                'metaTags': doc.get('metaTags', [])
            }
        ) for doc in collection.find({})
    ]
    document_store = InMemoryDocumentStore()
    print('-=-=-=-=-=-=-=-=-=-=-=-=-=')
    if documents:
        print('documents loaded: ' + str(len(documents)))
        first_doc = documents[0]
        print("Content:")
        print(first_doc.content)
        print("\nMetadata:")
        pprint(first_doc.meta)
    else:
        print("No documents found in haystack_docs.")
    print('-=-=-=-=-=-=-=-=-=-=-=-=-=')
    document_store.write_documents(documents)

    # Configure the pipeline
    pipe = Pipeline()
    pipe.add_component("retriever", InMemoryBM25Retriever(document_store=document_store))
    pipe.add_component("prompt_builder", PromptBuilder(template=template))
    pipe.add_component("llm", OllamaGenerator(
        model="llama3",
        url="http://localhost:11434/api/generate",
        generation_kwargs={
            "num_predict": 100,
            "temperature": 0.9,
        }
    ))

    # Connect components
    pipe.connect("retriever", "prompt_builder.documents")
    pipe.connect("prompt_builder", "llm")

    # Execute the pipeline
    query = "Given the context, give me a full list urls and their content with metaTags in meta that have name keyword"
    result = pipe.run({"prompt_builder": {"query": query},
                       "retriever": {"query": query}})

    print(result["llm"]["replies"])


if __name__ == "__main__":
    main()
