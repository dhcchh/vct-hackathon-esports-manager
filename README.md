# VCT Hackathon Submission

This is our repository for VCT eSports Manager Hackathon. It is made by [Hoo Kai Sng](https://www.linkedin.com/in/kai-sng-hoo-081a3622a/) , [Chan Ding Hao](https://www.linkedin.com/in/dhchan/), [Chua Wei Qi](https://www.linkedin.com/in/wei-qi-chua/) and [Yip Kai Men](https://www.linkedin.com/in/yipkaimen/). 

The goal is to support the scouting and recruitment process for VALORANT eSports teams using an LLM-powered digital assistant. The assistant helps build optimal teams by answering questions and analysing. 
[Link to the app on Streamlit Cloud](https://vct-hackathon-bot-kwjf4xyujwrvhntrmnp55i.streamlit.app/)

# Project Layout 
```
vct-chatbot-repository/
├── src/
│   ├── bedrock-agent-action-group-lambda.py
│   ├── bedrock-agent-action-group-openapi.yaml
│   └── upsert.py
│   └── retrieve_data.py
│   └── convert_data_to_json.py
├── services/
│   └── bedrock_agent_runtime.py
├── data/
│   └── source-and-metadata-files.zip
├── .gitignore
├── README.md
├── app.py
└── requirements.py
```

# Model Architecture 
Core Architecture of the VCT Hackathon Project. 

1. **Amazon Bedrock**  
   Provides **generative AI** capabilities for retrieving and generating answers based on queries related to team compositions, player roles, and performance metrics. AI Models used are:
   - Embedding Cohere English v3
   - Claude Haiku 3.0 LLM 

3. **Pinecone**  
   A **vector database** for storing and retrieving embeddings. Used to handle player and metadata embeddings efficiently, enabling fast and accurate responses to queries. We use Pinecone as it is the most cost effective option 

4. **Amazon S3**  
   Used for **storing data** and other files in an accessible bucket. The data is fetched, processed, and used for embedding and retrieval.

5. **AWS Lambda**  
   A **serverless compute service** that automates data processing tasks, like fetching data from the S3 bucket and triggering other processes in response to events, enabling seamless integration of the various services.

6. **Streamlit**  
   A **frontend interface** for user interaction. It powers a chat interface where users can ask questions and receive real-time team recommendations and player insights.

This core architecture integrates AI, database, frontend, and cloud storage components to deliver team building recommendations and player performance analysis. A visualisation of the overall architecture is provided below 

![RAG-architechture](https://github.com/user-attachments/assets/7e607642-563f-4533-abd4-4e97120515c9)

# Data Sources 

1. **Liquipedia**  
   The primary source of player data, including player names, teams, roles, and agents played. Liquipedia provides detailed information on player stats, team rosters, and tournament performances, which is critical for evaluating player performance and making team composition decisions. We call the Liquipedia API to pull data from the website.

2. **VALORANT Esports Videos and Forums**  
   Regional playstyles and strategic tendencies are inferred from community discussions and esports videos. This qualitative data helps define how different regions approach the game, influencing how teams are formed based on playstyle compatibility.

3. **Country of Origin Data**  
   Player languages are assumed based on their country of origin, and other languages that a player might speak are imputed manually.


These sources provide the necessary data to build effective team compositions, assess player skills, and map regional playstyles for VALORANT eSports scouting.


