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
        {{ "materialName" : "amount" }}
        The amount should be in grams, and should be as much as accurate as possible
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

    return json.dumps(estimations)


# Return the amount of material contained into the object
def get_material_amount(material, device, conversation):
    # We ask a question to the llm
    llm_output = conversation({"material": material, "device": device})['text']

    # We expect that the output will be a json because we specified it into the prompt
    json_response = json.loads(llm_output)

    return json_response


if __name__ == '__main__':
    # Initialize the language model
    llm = init_llm()

    # Create a conversation used to interact with it
    conversation = get_conversation_to_extract_material_amount(llm)

    print(get_critical_raw_material_estimation('Samsung Galaxy FE', conversation))


