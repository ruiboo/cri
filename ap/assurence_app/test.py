import app

id = '11512NC0100031'
year = 2019
api_key = 'HCxdCLcJFiCBiQvRA8vW6gNSsnNTlLbc'

data = app.fetch_plan_data(id, year, api_key)

plan_id = data['plan']['moops'][0]['amount']

print(plan_id)