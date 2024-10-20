import boto3
import logging
import json
import random

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
                        'in':
                        {
                            'key': 'standings',
                            'value': ['1st', '2nd', '3rd', '4th', '1st-2nd', '1st-3rd', '1st-4th', '2nd-3rd', '2nd-4th', '3rd-4th']
                        }
                    }
                ]
            }
        }
    }
    return retrieval_config_league

def create_league_igl_player_retrieval_config(league, n): 
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
                            'key': 'igl',
                            'value': "true"
                        }
                    },
                    {
                        'in':
                        {
                            'key': 'standings',
                            'value': ['1st', '2nd', '3rd', '4th', '1st-2nd', '1st-3rd', '1st-4th', '2nd-3rd', '2nd-4th', '3rd-4th']
                        }
                    }
                ]
            }
        }
    }
    return retrieval_config_league

def create_league_role_player_retrieval_config(league, role, n): 
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
                            'key': 'igl',
                            'value': 'false'
                        }
                    },
                    {
                        'equals':
                        {
                            'key': 'role',
                            'value': role
                        }
                    },
                    {
                        'in':
                        {
                            'key': 'standings',
                            'value': ['1st', '2nd', '3rd', '4th', '1st-2nd', '1st-3rd', '1st-4th', '2nd-3rd', '2nd-4th', '3rd-4th']
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
                            'key': 'league',
                            'value': 'vct international'
                        }
                    },
                    {
                        'equals': 
                        {
                            'key': 'region',
                            'value': region
                        }
                    },
                    {
                        'in': 
                        {
                            'key': 'standings',
                            'value': ['1st', '2nd', '3rd', '4th', '1st-2nd', '1st-3rd', '1st-4th', '2nd-3rd', '2nd-4th', '3rd-4th']
                        }
                    }
                ]
            }
        }
    }
    return retrieval_config_region

def create_region_igl_player_retrieval_config(region, n):
    retrieval_config_region = {
        'vectorSearchConfiguration': {
            'numberOfResults': n,  # Adjust this value to get the top few
            'filter': {
                'andAll': [
                    {
                        'equals': 
                        {
                            'key': 'league',
                            'value': 'vct international'
                        }
                    },
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
                            'key': 'igl',
                            'value': 'true'
                        }
                    },
                    {
                        'in': 
                        {
                            'key': 'standings',
                            'value': ['1st', '2nd', '3rd', '4th', '1st-2nd', '1st-3rd', '1st-4th', '2nd-3rd', '2nd-4th', '3rd-4th']
                        }
                    }
                ]
            }
        }
    }
    return retrieval_config_region

def create_region_role_player_retrieval_config(region, role, n):
    retrieval_config_region = {
        'vectorSearchConfiguration': {
            'numberOfResults': n,  # Adjust this value to get the top few
            'filter': {
                'andAll': [
                    {
                        'equals': 
                        {
                            'key': 'league',
                            'value': 'vct international'
                        }
                    },
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
                            'key': 'igl',
                            'value': 'false'
                        }
                    },
                    {
                        'equals':
                        {
                            'key': 'role',
                            'value': role
                        }
                    },
                    {
                        'in': 
                        {
                            'key': 'standings',
                            'value': ['1st', '2nd', '3rd', '4th', '1st-2nd', '1st-3rd', '1st-4th', '2nd-3rd', '2nd-4th', '3rd-4th']
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

def lambda_handler(event, context):

    # Initialize the Bedrock agent client
    client = boto3.client('bedrock-agent-runtime')

    api_path = event['apiPath']
    player_retrieval_config = []
    roles = ['smoker', 'entry', 'flex', 'anchor', 'support']
    essential_roles = [0, 1]
    supplemental_roles = [2, 3, 4]

    match api_path:
        case '/get-team-by-league':
            query = event.get('query', 'Retrieve top-ranked players in a league to build a team.')
            try:
                logger.info(f"Received parameters: {event.get('parameters')}")
                parameters = event.get('parameters', [])
                
                # Check if there are parameters and extract the 'league'
                if not parameters or not any(param.get('name') == 'league' for param in parameters):
                    return {
                        "statusCode": 400,
                        "body": "League parameter is missing"
                    }

                league = next(param['value'].lower() for param in parameters if param.get('name') == 'league')
                logger.info(f"League extracted: {league}")
    
                league_igl_player_retrieval_config = (create_league_igl_player_retrieval_config(league, 16), 1)
                player_retrieval_config.append(league_igl_player_retrieval_config)
                # Essential Roles
                for role in essential_roles:
                    player_retrieval_config.append( (create_league_role_player_retrieval_config(league, roles[role], 16), 1) )
                # Supplemental Roles
                supp1 = random.choice(supplemental_roles)
                supp2 = random.choice(supplemental_roles)
                if supp1 == supp2:
                    player_retrieval_config.append( (create_league_role_player_retrieval_config(league, roles[supp1], 16), 2) )
                else:
                    player_retrieval_config.append( (create_league_role_player_retrieval_config(league, roles[supp1], 16), 1) )
                    player_retrieval_config.append( (create_league_role_player_retrieval_config(league, roles[supp2], 16), 1) )
            except Exception as e:
                return {
                    "statusCode": 400,
                    "body": "League parameter is missing"
                }
        case '/get-mixed-gender-team':
            query = event.get('query', 'Retrieve top-ranked players and mixed gender players to build a team')
            player_retrieval_config.append( (create_league_igl_player_retrieval_config('vct international', 16), 1) )
            n_gc = random.choice([2, 3])
            n_essen_gc_2 = random.choice([0, 1, 2])
            n_essen_gc_3 = random.choice([1, 2])
            match n_gc:
                case 2:
                    match n_essen_gc_2:
                        case 0:
                            player_retrieval_config.append( (create_league_role_player_retrieval_config('vct international', roles[0], 16), 1) )
                            player_retrieval_config.append( (create_league_role_player_retrieval_config('vct international', roles[1], 16), 1) )
                            supp1 = random.choice(supplemental_roles)
                            supp2 = random.choice(supplemental_roles)
                            if supp1 == supp2:
                                player_retrieval_config.append( (create_league_role_player_retrieval_config('vct game changers', roles[supp1], 16), 2) )
                            else:
                                player_retrieval_config.append( (create_league_role_player_retrieval_config('vct game changers', roles[supp1], 16), 1) )
                                player_retrieval_config.append( (create_league_role_player_retrieval_config('vct game changers', roles[supp2], 16), 1) )
                        case 1:
                            essen1 = random.choice(essential_roles)
                            essen2 = 1 - essen1
                            supp1 = random.choice(supplemental_roles)
                            supp2 = random.choice(supplemental_roles)
                            player_retrieval_config.append( (create_league_role_player_retrieval_config('vct game changers', roles[essen1], 16), 1) )
                            player_retrieval_config.append( (create_league_role_player_retrieval_config('vct game changers', roles[supp1], 16), 1) )
                            player_retrieval_config.append( (create_league_role_player_retrieval_config('vct international', roles[essen2], 16), 1) )
                            player_retrieval_config.append( (create_league_role_player_retrieval_config('vct international', roles[supp2], 16), 1) )
                        case 2:
                            player_retrieval_config.append( (create_league_role_player_retrieval_config('vct game changers', roles[0], 16), 1) )
                            player_retrieval_config.append( (create_league_role_player_retrieval_config('vct game changers', roles[1], 16), 1) )
                            supp1 = random.choice(supplemental_roles)
                            supp2 = random.choice(supplemental_roles)
                            if supp1 == supp2:
                                player_retrieval_config.append( (create_league_role_player_retrieval_config('vct international', roles[supp1], 16), 2) )
                            else:
                                player_retrieval_config.append( (create_league_role_player_retrieval_config('vct international', roles[supp1], 16), 1) )
                                player_retrieval_config.append( (create_league_role_player_retrieval_config('vct international', roles[supp2], 16), 1) )
                case 3:
                    match n_essen_gc_3:
                        case 1:
                            essen1 = random.choice(essential_roles)
                            essen2 = 1 - essen1
                            supp1 = random.choice(supplemental_roles)
                            supp2 = random.choice(supplemental_roles)
                            player_retrieval_config.append( (create_league_role_player_retrieval_config('vct game changers', roles[essen1], 16), 1) )
                            player_retrieval_config.append( (create_league_role_player_retrieval_config('vct international', roles[essen2], 16), 1) )
                            if supp1 == supp2:
                                player_retrieval_config.append( (create_league_role_player_retrieval_config('vct gamechangers', roles[supp1], 16), 2) )
                            else:
                                player_retrieval_config.append( (create_league_role_player_retrieval_config('vct game changers', roles[supp1], 16), 1) )
                                player_retrieval_config.append( (create_league_role_player_retrieval_config('vct game changers', roles[supp2], 16), 1) )
                        case 2:
                            supp1 = random.choice(supplemental_roles)
                            supp2 = random.choice(supplemental_roles)
                            player_retrieval_config.append( (create_league_role_player_retrieval_config('vct game changers', roles[0], 16), 1) )
                            player_retrieval_config.append( (create_league_role_player_retrieval_config('vct game changers', roles[1], 16), 1) )    
                            player_retrieval_config.append( (create_league_role_player_retrieval_config('vct game changers', roles[supp1], 16), 1) )
                            player_retrieval_config.append( (create_league_role_player_retrieval_config('vct international', roles[supp2], 16), 1) )                                       
        case '/get-cross-regional-team':
            query = event.get('query', 'Retrieve top-ranked players from different regions to build a team')
            regions = ['china', 'emea', 'americas', 'pacific']
            random.shuffle(regions)
            shuffled_regions = regions[:3]
            supp1 = random.choice(supplemental_roles)
            supp2 = random.choice(supplemental_roles)
            essen1 = random.choice(essential_roles)
            essen2 = 1 - essen1
            player_retrieval_config.append( (create_region_igl_player_retrieval_config(shuffled_regions[0], 16), 1) )
            player_retrieval_config.append( (create_region_role_player_retrieval_config(shuffled_regions[1], roles[essen1], 16), 1) )
            player_retrieval_config.append( (create_region_role_player_retrieval_config(shuffled_regions[2], roles[essen2], 16), 1) )
            if supp1 == supp2:
                player_retrieval_config.append( (create_region_role_player_retrieval_config(shuffled_regions[0], roles[supp1], 16), 2) )
            else:
                player_retrieval_config.append( (create_region_role_player_retrieval_config(shuffled_regions[0], roles[supp1], 16), 1) )
                player_retrieval_config.append( (create_region_role_player_retrieval_config(shuffled_regions[0], roles[supp2], 16), 1) )
        case '/get-semi-pro-team':
            query = event.get('query', 'Retrieve top-ranked players and semi-pro players to build a team')
            player_retrieval_config.append( (create_league_igl_player_retrieval_config('vct international', 16), 1) )
            supp1 = random.choice(supplemental_roles)
            player_retrieval_config.append( (create_league_role_player_retrieval_config('vct international', roles[supp1], 16), 1) )
            n_gc = random.choice([1, 2])
            essen1 = random.choice(essential_roles)
            essen2 = 1 - essen1
            supp2 = random.choice(supplemental_roles)
            player_retrieval_config.append( (create_league_role_player_retrieval_config('vct challengers', roles[essen1], 16), 1) )
            player_retrieval_config.append( (create_league_role_player_retrieval_config('vct game changers', roles[essen2], 16), 1) )
            match n_gc:
                case 1:
                    player_retrieval_config.append( (create_league_role_player_retrieval_config('vct challengers', roles[supp2], 16), 1) )
                case 2:
                    player_retrieval_config.append( (create_league_role_player_retrieval_config('vct game changers', roles[supp2], 16), 1) )
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

        # Text retrieval
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

        # Player retrieval
        for retrieval_config, n in player_retrieval_config:
            player_result = client.retrieve(
                knowledgeBaseId = knowledge_base_id,
                retrievalConfiguration = retrieval_config,
                retrievalQuery = {
                    "text": query
                }
            )
            # Retrieve all results and shuffle them
            all_entries = player_result['retrievalResults']
            random.shuffle(all_entries)
            # Return the first `n` entries after shuffling
            shuffled_entries = all_entries[:n]

            logger.info(f"Retrieval configuration: {player_retrieval_config}")
            logger.info(f"Retrieve operation response: {player_result}")
            for index, doc in enumerate(shuffled_entries, start = 1):
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