import json
from tqdm import tqdm
from dictdiffer import diff
from rich.pretty import pprint


from phi.agent import Agent
from phi.model.ollama import Ollama

extract_agent = Agent(
    #model=Ollama(id="sroecker/nuextract-tiny-v1.5"),
    #model=Ollama(id="iodose/nuextract-v1.5", options={"temperature": 0}),
    #model=Ollama(id="sroecker/nuextract-v1.5-smol", options={"temperature": 0}),
    model=Ollama(id="sroecker/nuextract-v1.5-smol:q8_0", options={"temperature": 0}),
    description="You extract information.",
    structured_outputs=True,
)

def predict_nuextract(input_text):
    template = """
    {
        "Customer": {
            "Name": "",
            "Address": "",
            "Policy Number": "",
            "Telephone Number": "",
            "Email Address": "",
        },
        "Case": {
            "Accident Location": "",
            "Date and Time": "",
        }
    }
    """
    template = f"""<|input|>\n ### Template:\n{template}\n### Text:\n{input_text}\n\n<|output|>"""

    return template

# Load cases
cases_jsonl = 'claims/insurance_claim_reports.jsonl'
cases = []

# Open the JSONL file and load each line as a dictionary
with open(cases_jsonl, 'r', encoding='utf-8') as file:
    for line in file:
        cases.append(json.loads(line.strip()))
#pprint(cases)


def normalize_dict1(d):
    return {
        'Name': d['customer_name'],
        'Address': d['customer_address'],
        'Policy Number': d['policy_number'],
        'Telephone Number': d['phone_number'],
        'Email Address': d['customer_email'],
    }

def normalize_dict2(d):
    return {
        'Name': d['Customer'].get('Name', ''),
        'Address': d['Customer'].get('Address', ''),
        'Policy Number': d['Customer'].get('Policy Number'),
        'Telephone Number': d['Customer'].get('Telephone Number', ''),
        'Email Address': d['Customer'].get('Email Address', ''),
    }

for case in tqdm(cases):
    res = extract_agent.run(predict_nuextract(case['description']), stream=False)
    try:
        #ex_case = json.loads(res.content)
        # https://stackoverflow.com/a/72993909
        ex_case = json.loads(rf"{res.content}")
    except:
        pprint("Failed to parse: " + res.content)
    n_dict1 = normalize_dict1(case)
    n_dict2 = normalize_dict2(ex_case)
    diff_res = diff(n_dict1, n_dict2)
    pprint(list(diff_res))
