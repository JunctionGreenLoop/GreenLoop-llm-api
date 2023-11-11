from langchain import PromptTemplate, OpenAI, LLMChain, GoogleSearchAPIWrapper
from dotenv import load_dotenv
import os
import json
from utils import ThreadWithResult


# Initialize the llm model by loading the auth_keys from the env file
def init_llm(temperature=0):
    load_dotenv()
    llm = OpenAI(temperature=temperature, openai_api_key=os.getenv('OPENAI_API_KEY'))
    return llm


# Starting from the llm generates a conversation to extract the material amount
def get_conversation_to_extract_material_amount(llm):
    # Prepares the parametrized prompt that will be used
    prompt = PromptTemplate.from_template('''
        What is the amount of {material} contained in a {device}

        Format the output as json like
        {{ "materialCode": {material} , "amount": amount}}
        The amount should be in grams, and should be as much as accurate as possible.
        Do not specify the unit of measure in the output
        ''')

    # Creates the conversation object
    conversation = LLMChain(
        llm=llm,
        prompt=prompt,
        # verbose=True
    )

    return conversation


# Retrieves from a file the list of critical raw materials
def get_critical_raw_material_list():
    # Updated list: https://rmis.jrc.ec.europa.eu/eu-critical-raw-materials
    with open("../resources/criticalRawMaterialsTesting.txt") as f:
        crm_list = f.read().splitlines()
    return crm_list


# Given a device returns the estimation of all the critical raw materials contained in it
def get_critical_raw_material_estimation(device, conversation):
    # Retrieve the list of critical raw materials
    crm_list = get_critical_raw_material_list()

    # Loop through the crms and ask and estimation to the llm
    threads = []
    for crm in crm_list:
        # Some threading is needed to avoid incredibly long waiting times
        thread = ThreadWithResult(target=get_material_amount, args=(crm, device, conversation))
        thread.start()
        threads.append(thread)

    # Wait for all thread to finish and collect the results
    estimations = []
    for thread in threads:
        thread.join()
        estimations.append(thread.result)

    return estimations


# Return the amount of material contained into the object
def get_material_amount(material, device, conversation):
    # We ask a question to the llm
    llm_output = conversation({"material": material, "device": device})['text']

    # We expect that the output will be a json because we specified it into the prompt
    json_response = json.loads(llm_output)

    return json_response


# Given a device, generate the commercial information (common name and manufacturer)
def estimate_commercial_info(llm, device):
    # Prepares the parametrized prompt that will be used
    prompt = PromptTemplate.from_template('''
            What are the manufacturer and the commercial name of {device}?

            Format the output as json like
            {{ "manufacturer" : "manufacturerName", "commercialName": "commercialName"}}
            ''')

    # Creates the conversation object
    conversation = LLMChain(
        llm=llm,
        prompt=prompt,
        # verbose=True
    )

    # Executes the query and returns the result
    return json.loads(conversation(device)['text'])


# Given a device, estimate the related Co2 emissions
def estimate_co2_emissions(llm, device):
    # Prepares the parametrized prompt that will be used
    prompt = PromptTemplate.from_template('''
            What is the carbon footprint of the {device}?
    
            Format the output as json like
            {{ "co2Emission" : value}}
            
            The value must be in Kg.
            Do not specify the unit of measure in the output
            ''')

    # Creates the conversation object
    conversation = LLMChain(
        llm=llm,
        prompt=prompt,
        # verbose=True
    )

    # Executes the query and returns the result
    co2_estimation = conversation(device)['text']
    return json.loads(co2_estimation)


# Given the llm's crm json output, adapt it to the standard by generating the missing fields (co2 emissions...)
def standardize_crm_estimation(device_id, json_output, llm):
    formatted_output = {
      "name": device_id,
      "materials": json_output,
    }

    # Add to the output the estimation of carbon emissions
    formatted_output.update(estimate_co2_emissions(llm, device_id))

    # Add to the output the estimation of commercial names and manufacturer
    formatted_output.update(estimate_commercial_info(llm, device_id))

    return formatted_output


# Given a device, return all the api information
def generate_api_info(device, llm):
    # Create a conversation used to interact with the llm
    conversation = get_conversation_to_extract_material_amount(llm)

    # Estimate the number of raw materials
    crm_estimation = get_critical_raw_material_estimation(device, conversation)

    # Standardize the output adding the missing fields
    return standardize_crm_estimation(device, crm_estimation, llm)


if __name__ == '__main__':
    device = "Iphone 8"

    # Initialize the language model
    llm = init_llm()

    print(generate_api_info(device, llm))