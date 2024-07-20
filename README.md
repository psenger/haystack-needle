---
tags:
  - mongodb
  - python
  - Haystack
  - ollama
  - how-to
---

# haystack-needle - MongoDB Web Crawl with Haystack and Ollama  
> haystack.deepset.ai, MongoDb, Python, Ollama

This project demonstrates how to set up a web crawl data processing pipeline using MongoDB, Haystack, and Ollama. The primary purpose is to fetch documents from a MongoDB replica set, process them, and retrieve information based on specific queries using the Haystack framework.  
  
## Requirements  
  
- Python 3.8+  
- MongoDB  
- Haystack  
- Ollama  
  
## Project Structure  
  
- `main.py`: The main script that sets up and runs the data processing pipeline.  
  
## Setup Instructions  
  
1. **Clone the Repository**  
    ```bash  
    git clone https://github.com/psenger/haystack-needle  
    cd haystack-needle
    ```  
  
2. **Install Dependencies**  
    ```bash  
    pip install -r requirements.txt  
    ```  
  
3. **Configure MongoDB Connection**  
  
    Make sure your MongoDB replica set is running and accessible. The URI in the script is set to:  
    ```python  
    uri = "mongodb://mongo-1:27017,mongo-2:27117,mongo-3:27217/web-crawl"  
    ```  
  
    Modify this as per your MongoDB setup.  
  
4. **Run the Script**  
  
    Execute the `main.py` script to fetch documents from MongoDB, process them with Haystack, and run queries.  
    ```bash  
    python main.py  
    ```  
  
## Components  
  
### MongoDB  
  
The script connects to a MongoDB replica set without authentication. Ensure your MongoDB instance is configured correctly.  
  
### Haystack  
  
Haystack is used for setting up the document store and the pipeline. Key components include:  
  
- **InMemoryDocumentStore**: Stores documents in memory for retrieval.  
- **InMemoryBM25Retriever**: Retrieves relevant documents based on BM25 algorithm.  
- **PromptBuilder**: Builds the prompt for the query.  
- **OllamaGenerator**: Generates responses using the Ollama model.  
  
### Ollama  
  
Ollama is used to generate responses based on the context and query provided. The model is specified as `llama3` and runs on a local server.  
  
## Script Overview  
  
1. **MongoDB Connection**  
  
    Connects to MongoDB and fetches documents:  
    ```python  
    client = MongoClient(uri_with_options)  
    db = client['web-crawl']  
    collection = db['pages']  
    ```  
  
2. **Document Processing**  
  
    Processes and converts MongoDB documents into Haystack `Document` objects:  
    ```python  
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
    ```  
  
3. **Pipeline Configuration**  
  
    Sets up the Haystack pipeline with retriever, prompt builder, and Ollama generator:  
    ```python  
    pipe = Pipeline()  
    pipe.add_component("retriever", InMemoryBM25Retriever(document_store=document_store))  
    pipe.add_component("prompt_builder", PromptBuilder(template=template))  
    pipe.add_component("llm", OllamaGenerator(  
        model="llama3",  
        url="http://localhost:11434/api/generate",  ---
tags:
  - mongodb
  - python
  - Haystack
  - ollama
  - how-to
---
# MongoDB Web Crawl with Haystack and Ollama  
  
This project demonstrates how to set up a web crawl data processing pipeline using MongoDB, Haystack, and Ollama. The primary purpose is to fetch documents from a MongoDB replica set, process them, and retrieve information based on specific queries using the Haystack framework.  
  
## Requirements  
  
- Python 3.8+  
- MongoDB  
- Haystack  
- Ollama  
  
## Project Structure  
  
- `main.py`: The main script that sets up and runs the data processing pipeline.  
  
## Setup Instructions  
  
1. **Clone the Repository**  
        generation_kwargs={  
            "num_predict": 100,  
            "temperature": 0.9,  
        }  
    ))  
    ```  
  
4. **Executing the Pipeline**  
  
    Runs the pipeline with a specific query:  
    ```python  
    query = "Given the context, give me a full list urls and their content with metaTags in meta that have name keyword"  
    result = pipe.run({"prompt_builder": {"query": query},  
                       "retriever": {"query": query}})  
    ```  
  
## License  
  
This project is licensed under the Apache License Version 2.0. See the [LICENSE](LICENSE) file for more details.  
  
## Contributing  
  
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.  
  
## Contact  
  
For any inquiries or support, please contact on [LinkedIn](https://www.linkedin.com/in/philipsenger/).