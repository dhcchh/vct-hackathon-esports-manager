import boto3
import logging
import json

# Add this at the top of your script to enable logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def create_league_player_retrieval_config(league, n): 
    # Can be 'vct international' or 'vct challengers' or 'vct game changers'
    retrieval_config_league = {
        'vectorSearchConfiguration': {
            'numberOfResults': n,  # Adjust this value to get the top few
            'filter': {
                'andAll': [
                    {
                        'equals': 
                        {
                            'key': 'league',
                            'value': league
                        }
                    },

                    {
                        'equals':
                        {
                            'key': 'standings',
                            'value': '1st'
                        }
                    }
                ]
            }
        }
    }
    return retrieval_config_league

def create_region_player_retrieval_config(region, n):
    retrieval_config_region = {
        'vectorSearchConfiguration': {
            'numberOfResults': n,  # Adjust this value to get the top few
            'filter': {
                'andAll': [
                    {
                        'equals': 
                        {
                            'key': 'region',
                            'value': region
                        }
                    },
                    {
                        'equals': 
                        {
                            'key': 'standings',
                            'value': '1st'
                        }
                    }
                ]
            }
        }
    }
    return retrieval_config_region

text_retrieval_config = {
    'vectorSearchConfiguration': {
        'numberOfResults': 10, # All the data needed is split into 10 entries, retrieve all of them everytime
        'filter': {
            'in': 
            {
                'key': 'category',   # only text data have the 'category' attribute
                'value': ['team_role', 'regional_playstyles']
            }
        }
    }
}

import boto3

def lambda_handler(event, context):

    # Initialize the Bedrock agent client
    client = boto3.client('bedrock-agent-runtime')

    api_path = event['apiPath']
    player_retrieval_config = []

    match api_path:
        case '/get-team-by-league':
            query = event.get('query', 'Retrieve top-ranked players in a league/region to build a team.')
            try:
                league = event['parameters'][0]['value'].lower()
                league_player_retrieval_config = create_league_player_retrieval_config(league, 20)
                player_retrieval_config.append(league_player_retrieval_config)
            except Exception as e:
                return {
                    "statusCode": 400,
                    "body": "League parameter is missing"
                }
        case '/get-mixed-gender-team':
            query = event.get('query', 'Retrieve top-ranked players and mixed gender players to build a team')
            player_retrieval_config.append(create_league_player_retrieval_config('vct game changers', 10))
            player_retrieval_config.append(create_league_player_retrieval_config('vct international', 10))
        case '/get-cross-regional-team':
            query = event.get('query', 'Retrieve top-ranked players from different regions to build a team')
            player_retrieval_config.append(create_region_player_retrieval_config('china', 5))
            player_retrieval_config.append(create_region_player_retrieval_config('emea', 5))
            player_retrieval_config.append(create_region_player_retrieval_config('americas', 5))
            player_retrieval_config.append(create_region_player_retrieval_config('pacific', 5))
        case '/get-semi-pro-team':
            query = event.get('query', 'Retrieve top-ranked players and semi-pro players to build a team')
            player_retrieval_config.append(create_league_player_retrieval_config('vct game changers', 10))
            player_retrieval_config.append(create_league_player_retrieval_config('vct challengers', 10))
            player_retrieval_config.append(create_league_player_retrieval_config('vct international', 5))
        case _:
            return {
                "statusCode": 400,
                "body": "Invalid API Path"
            }

    # Define the knowledge base ID (replace 'kbi' with your actual knowledge base ID)
    knowledge_base_id = 'TCESP6AION'  # Replace with actual knowledge base ID

    # Perform the retrieval
    try:
        # Process the retrieved results and format the output
        response_data = []

        text_result = client.retrieve(
            knowledgeBaseId = knowledge_base_id,
            retrievalConfiguration = text_retrieval_config,
            retrievalQuery = {
                "text": "Provide insights on team strategy and hypothesize team strengths and weaknesses"
            }
        )
        logger.info(f"Retrieval configuration: {text_retrieval_config}")
        logger.info(f"Retrieve operation response: {text_result}")
        for index, doc in enumerate(text_result['retrievalResults'], start = 1):
            response_data.append({
                "content": doc['content'],
                "metadata": doc['metadata']
            })

        for retrieval_config in player_retrieval_config:
            player_result = client.retrieve(
                knowledgeBaseId = knowledge_base_id,
                retrievalConfiguration = retrieval_config,
                retrievalQuery = {
                    "text": query
                }
            )
            logger.info(f"Retrieval configuration: {player_retrieval_config}")
            logger.info(f"Retrieve operation response: {player_result}")
            for index, doc in enumerate(player_result['retrievalResults'], start = 1):
                response_data.append({
                    "content": doc['content'],
                    "metadata": doc['metadata']
                })

        response_body = {
            "application/json": {
                "body": json.dumps(response_data)
            }
        }

        action_response = {
            'actionGroup': event['actionGroup'],
            'apiPath': event['apiPath'],
            'httpMethod': event['httpMethod'],
            'httpStatusCode': 200,
            'responseBody': response_body
        }

        sessionAttributes = event['sessionAttributes']
        promptSessionAttributes = event['promptSessionAttributes']
        api_response = {
            "messageVersion": "1.0",
            "response": action_response,
            "sessionAttributes": sessionAttributes,
            "promptSessionAttributes": promptSessionAttributes
        }

        return api_response

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error retrieving data: {str(e)}"
        }