from crawlbase import CrawlingAPI
import json

# Initialize the Crawling API with your Crawlbase Normal token
api = CrawlingAPI({ 'token': 'rkcSMegJId6B-Wx6R9WNCw' })

# URL of the Google search page you want to scrape
google_search_url = 'https://www.google.com/search?q='+input("Enter query")

# options for Crawling API
options = {
 'scraper': 'google-serp'
}

# Make a request to scrape the Google search page with options
response = api.get(google_search_url, options)

# Check if the request was successful
if response['status_code'] == 200 and response['headers']['pc_status'] == '200':
    # Loading JSON from response body after decoding byte data
    response_json = json.loads(response['body'].decode('latin1'))
    response_json=response_json["body"]["searchResults"]
    # pretty printing response body
    # print(response_json)
    full_results=""
    for i in range (min(len(response_json),4)):
        # print(response_json[i])
        full_results+=response_json[i]["description"] 

    print(full_results)

else:
    print("Failed to retrieve the page. Status code:", response['status_code'])
