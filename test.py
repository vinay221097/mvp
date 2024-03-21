import requests

API_URL = "https://api-inference.huggingface.co/models/mgrella/autonlp-bank-transaction-classification-5521155"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()
	
output = query({
	"inputs": "fast payment with debit card",
})

print(output)