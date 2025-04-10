import requests

jwt_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJBS0IyMTQ2NC5DT1JURVhTRUFSQ0hUT0tFTi5TSEEyNTY6bDBoS01WRHkwRlRJQXA3NndDZDM0SGQzL0s5dHVYQWpoNEpJMlk2TnBUND0iLCJzdWIiOiJBS0IyMTQ2NC5DT1JURVhTRUFSQ0hUT0tFTiIsImlhdCI6MTcyNzI0ODE1OSwiZXhwIjoxNzI3MzM0NTU5fQ.WKAlZlPU4hL1iShCQaHzxtJ0CS-CZ6J5esHjj4HKIBpsYxRcp-zyAXaQ0b0h-X8UsrDM6BzNKaIPlpYDtTIZxyZELJds59eBR2uVMripGEXPdh3nKJkeXSXvfRIwmjPE-2TBVRbr_xmRxytsM-qV7zeo_148DibSek7e_Mmwl0nGyVXf9hRGFEaAmHCj4zqzQrHRsWiWTgkMoTyGyonsEF97sOk9FYOmnjfDP-QCbKgmPMfmZGK5_yBuG3-0GF_L0Poo5-OyRRhCzelk6c2c-88PwVKQiEiOCSsYdey8ScSv2T7nNX35WDd2NDpxdsEfTzU_sR8O-7v6ajAtrcBPTw'
# Snowflake account and API endpoint

account = "tufbwjl-qeb33118"
api_endpoint = f"https://{account}.snowflakecomputing.com/api/v2/statements"

# # SQL statement to call your stored procedure
sql_statement = "CALL cortex_search_procedure('Explain Oncology', 'RELATIVE_PATH', 'Cardiology_Comprehensive_Overview.pdf', 5);"

# The rest of your code remains the same
payload = {
"statement": sql_statement,
"timeout": 60,
"database": "CORTEX_SEARCH_DB",
"schema": "CORTEX_SEARCH_SCHEMA",
"warehouse": "CORTEX_SEARCH_WH",
"role": "CORTEX_SEARCH_TOKEN"
}

# Set up the headers (use Bearer token format)
headers = {
    "Content-Type": "application/json",
    "X-Snowflake-Authorization-Token-Type" :"KEYPAIR_JWT",
    "Authorization": f"Bearer {jwt_token}"  # Use Bearer token format for JWT
}

# Send the request
response = requests.post(api_endpoint, json=payload, headers=headers)

# Handle the response
if response.status_code == 200:
    result = response.json()
    print("Stored procedure executed successfully:", result)
else:
    print(f"Error executing stored procedure (Status Code: {response.status_code}):", response.text)



