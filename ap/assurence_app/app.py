import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin
import subprocess
import json

app = Flask(__name__)
CORS(app)

api_key = "HCxdCLcJFiCBiQvRA8vW6gNSsnNTlLbc"

def fetch_plan_data(plan_id, year, api_key):
    url = f"https://marketplace.api.healthcare.gov/api/v1/plans/{plan_id}?year={year}"
    headers = {
        "apikey": api_key
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # raise an exception for HTTP errors
        data =  response.json()  # No need to use json.loads() as requests can decode JSON
        return data
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}, Response: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

    return None

def find_phrases(data, phrases, path=None, problematic_clauses=None):
    if path is None:
        path = []
    if problematic_clauses is None:
        problematic_clauses = []

    phrases = [phrase.lower() for phrase in phrases]

    if isinstance(data, dict):
        for key, value in data.items():
            new_path = path + [key]
            for phrase in phrases:
                if phrase in str(key).lower() or phrase in str(value).lower():
                    problematic_clauses.append({'path': new_path, 'data': value, 'phrase': phrase})
            if isinstance(value, (dict, list)):
                find_phrases(value, phrases, new_path, problematic_clauses)

    elif isinstance(data, list):
        for index, item in enumerate(data):
            new_path = path + [str(index)]
            for phrase in phrases:
                if phrase in str(item).lower():
                    problematic_clauses.append({'path': new_path, 'data': item, 'phrase': phrase})
            if isinstance(item, (dict, list)):
                find_phrases(item, phrases, new_path, problematic_clauses)

    return problematic_clauses

def parse_plan_data(data):

    print(data)

    plan_info = {}
    
    # Directly accessing keys; will raise KeyError if 'plan' or any sub-key is not present
    plan_info['id'] = data['plan']['id']
    plan_info['name'] = data['plan']['name']
    plan_info['metal_level'] = data['plan']['metal_level']
    plan_info['type'] = data['plan']['type']
    plan_info['state'] = data['plan']['state']
    
    # Pricing & Premium Information
    plan_info['premium'] = data['plan']['premium']
    plan_info['ehb_premium'] = data['plan']['ehb_premium']
    plan_info['pediatric_ehb_premium'] = data['plan']['pediatric_ehb_premium']
    plan_info['aptc_eligible_premium'] = data['plan']['aptc_eligible_premium']

    # Extracting the benefits details
    benefits_list = []
    for benefit in data['plan']['benefits']:
        benefit_data = {
            'name': benefit['name'],
            'covered': benefit['covered'],
        }
        benefits_list.append(benefit_data)

    # Combining the main plan details with the benefits details
    combined_data = {
        'plan_details': plan_info,
        'benefits': benefits_list
    }

    return combined_data

def get_problematic_clauses_score(plan_data, problematic_phrases):
    pc_score = 100
    phrase_presence = find_phrases(plan_data, problematic_phrases)
    severity_scores = {
        'catastrophic': 30,
        'limited': 20,
    }
    for phrase_dict in phrase_presence:
        for phrase in problematic_phrases:
            if phrase in str(phrase_dict['data']).lower():
                pc_score -= severity_scores.get(phrase, 0)

    pc_score = max(pc_score, 0)
    return pc_score

def get_price_score(plan_data):
    price_score = 10000
    premium = plan_data['plan']['premium']
    moop = plan_data['plan']['moops'][0]['amount']
    base = premium + moop
    price_score = base/100
    return price_score

def get_issuer_rating(plan_data):
    issuer_id = plan_data['plan']['issuer']['name']
    issuer_ratings = {
        'Health Insurance': {'2022': 73, '2023': 76},
        'Humana': {'2022': 77, '2023': 82},
        'All Others': {'2022': 72, '2023': 78},
        'United Health': {'2022': 75, '2023': 78},
        'Aetna (CVS Health)': {'2022': 74, '2023': 77},
        'Blue Cross Blue Shield': {'2022': 73, '2023': 75},
        'Centene': {'2022': 72, '2023': 75},
        'Kaiser Permanente': {'2022': 73, '2023': 73},
        'Cigna': {'2022': 71, '2023': 72},
    }

    # Check if the issuer_id is in the mapping
    if issuer_id in issuer_ratings:
        return issuer_ratings[issuer_id]['2023']
    else:
        return issuer_ratings['All Others']['2023']

def calculate_plan_grade(plan_data, problematic_phrases):
    # compute scores
    problematic_clauses_score = get_problematic_clauses_score(plan_data, problematic_phrases)
    price_score = get_price_score(plan_data)
    issuer_rating = get_issuer_rating(plan_data)

    grade = (problematic_clauses_score + price_score + issuer_rating)/3

    return grade

@app.route('/test', methods=['GET', 'POST'])
@cross_origin(origin='http://localhost:3000', headers=['Content-Type', 'Authorization'])
def home():
    if request.method == 'POST':
        data = request.get_json()  # Use to get JSON data
        plan_id = data['plan_id']
        year = data['year']
        problematic_phrases = ['catastrophic', 'limited']

        plan_data = fetch_plan_data(plan_id, year, api_key)
        plan_name = plan_data['plan']['name']
        issuer_rating = get_issuer_rating(plan_data)
        
        if plan_data is None: 
            return "Failed to fetch plan data", 500
        
        problematic_clauses = find_phrases(plan_data, problematic_phrases)
        price_score = get_price_score(plan_data)

        response_data = {
            "grade": calculate_plan_grade(plan_data, problematic_phrases),
            "problematic_clauses": problematic_clauses,
            "price_score": price_score,
            "issuer_rating": issuer_rating,
            "plan_name": plan_name
        }

        # Pass the raw plan_data to the template instead of processed_data
        response = jsonify(response_data)
        # response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        print("this should never happen")
        return jsonify({"hello": "world"})
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
