import openai
import json
import os
from dotenv import load_dotenv
import requests

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
rapid_api_key = os.getenv("X-RapidAPI-Key")

GPT_MODEL = "gpt-3.5-turbo-0613"
#GPT_MODEL = "gpt-4"

function_descriptions = [
    {
        "name": "get_movie_details_by_title",
        "description": "Get details about the movie by the title passed in as parameter",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "the title of the movie"
                },
            },
            "required": ["title"]
        }
    },
    {
        "name": "get_my_bank_balance",
        "description": "Returns the amount of money I have in my bank",
        "parameters": {
            "type": "object",
            "properties": {
                "accountId": {
                    "type": "string",
                    "description": "the account id that holds all my money"
                },
                "routingNumber": {
                    "type": "string",
                    "description": "the routing number of the bank that has the account that holds all my money"
                },
            },
            "required": ["accountId", "routingNumber"]
        }
    },
    {
        "name": "get_routing_number_for_bank",
        "description": "Returns the routing number of the bank given the name of the bank",
        "parameters": {
            "type": "object",
            "properties": {
                "bankName": {
                    "type": "string",
                    "description": "the name of the bank"
                }
            },
            "required": ["bankName"]
        }
    },
    {
        "name": "where_is_all_my_money",
        "description": "Returns bank name where my money is stored!",
        "parameters": {
            "type": "object",
            "properties": {
            }
        }
    },
    {
        "name": "get_my_account_number",
        "description": "Returns my account number",
        "parameters": {
            "type": "object",
            "properties": {
            }
        }
    }
]


def get_my_bank_balance(accountId, routingNumber):
    # go out and get it!
    # For now:
    print("---->Returning bank balance for accountId", accountId, " and routingNumber", routingNumber)
    return {"balance" : "12500", "currency" : "USD"}

def get_routing_number_for_bank(bankName) :
    # go out and get it!
    # For now:
    print("--->Returning routingNumber for bank", bankName)
    return {"routingNumber": "1234ABC"}

def get_my_account_number() :
    # go out and get it!
    # For now:
    print("--->Returning account number")
    return {"accountId": "AC_NUM_1234"}

def where_is_all_my_money():
    # go out and get it!
    # For now:
    print("---->Returning a random bank name")
    return {"bankName": "Chase"}



def function_call(ai_response):
    function_call = ai_response["choices"][0]["message"]["function_call"]
    function_name = function_call["name"]
    print("--------->", function_name)
    arguments = function_call["arguments"]
    if function_name == "where_is_all_my_money":
        return where_is_all_my_money()
    elif function_name == "get_routing_number_for_bank":
        bankName = eval(arguments).get("bankName")
        return get_routing_number_for_bank(bankName)
    elif function_name == "get_my_account_number":
        return get_my_account_number()    
    elif function_name == "get_my_bank_balance":
        routingNumber = eval(arguments).get("routingNumber")
        accountId = eval(arguments).get("accountId")
        return get_my_bank_balance(accountId, routingNumber)    
    else:
        return
        

def ask_function_calling(query):
    messages = [{"role": "user", "content": query}]

    response = openai.ChatCompletion.create(
        model= GPT_MODEL,
        messages=messages,
        functions = function_descriptions,
        function_call="auto"
    )

    print("first", response)

    while response["choices"][0]["finish_reason"] == "function_call":
        function_response = function_call(response)
        messages.append({
            "role": "function",
            "name": response["choices"][0]["message"]["function_call"]["name"],
            "content": json.dumps(function_response)
        })

        print("messages: ", messages) 

        response = openai.ChatCompletion.create(
            model= GPT_MODEL,
            messages=messages,
            functions = function_descriptions,
            function_call="auto"
        )   

        print("subsequent: ", response) 
    else:
        print("pfft", response)

# This uses a random accountId and a routing number instead of using my custom functions
# user_query = "What are my savings in the bank that I store my money in?" 

# Works! -> "Your account number is AC_NUM_1234 and the routing number for your bank is 1234ABC. The savings in your bank account is $12,500."
# user_query = "First determine my account number and my routing number and then use that info to determine what are my savings in the bank that I store my money in?"

# Partial: Got my bank name but used fake account number and routing number: "Your savings in the bank where you store your money, which is Chase, is $12,500."
# user_query = "What are my savings in the bank that I store my money in? Don't make assumptions about my accountId and my routing number" 

# Works! -> "Based on the information provided, your account number is AC_NUM_1234 and your routing number is 1234ABC. Your current savings in the bank is $12,500.\n\nTo determine if you can buy a car worth $13,000 with your current savings, we need to compare the savings with the cost of the car. \n\nSince your savings is $12,500, which is less than $13,000, you will not be able to buy the car with your current savings. You need an additional $500 to meet the cost of the car."
user_query = "If all I wanted in life was a car worth $13000, could I buy that with my current savings? First determine my account number, bank name and my routing number and then use that info to determine what are my savings in the bank. Why or why not?"
ask_function_calling(user_query)
