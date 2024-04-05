from serpapi import GoogleSearch
import json

def search_answer(question):
    params = {
      "api_key": "cff2d3fe0b668f8cf2692b027044308708399975dda29a049de5ff0d5a56c205",
      "engine": "google",
      "q": question,
      "google_domain": "google.com",
      "gl": "us",
      "hl": "en"
    }


    res=""
    try:
        search = GoogleSearch(params)
        response = search.get_dict()
        # print(response)
        if "description" in response.keys():
            full_results=response["description"]
        elif "organic_results" in response.keys():
            response_json = response
            response_json=response_json["organic_results"]
            # print(response_json)
            full_results=""
            for i in range (min(len(response_json),4)):
                # print(response_json[i])
                full_results+=response_json[i]["snippet"] 
            system_prompt="You are a brilliant assistant and help in answering questions for the user."
            prompt_input=f"""Data:{full_results}
                            Based on the given data above can you answer {question}"""

            res= generate_text(prompt_input,system_prompt)
    except Exception as r:
        print(r)
        res=get_backup_answer(question)
    return res


question="latest news on microsoft"

print(search_answer(question))