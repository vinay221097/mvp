import warnings
warnings.filterwarnings('ignore')

from langchain.document_loaders.csv_loader import CSVLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain_community.document_loaders import UnstructuredFileLoader

from unstructured.cleaners.core import remove_punctuation,clean,clean_extra_whitespace
from unstructured.cleaners.core import clean_extra_whitespace
from langchain.schema import HumanMessage, SystemMessage
from deep_translator import GoogleTranslator

from utils import *
from model2 import *
ittranslator= GoogleTranslator(source='en', target='it')
entranslator= GoogleTranslator(source='it', target='en')
# Define the path for generated embeddings
DB_FAISS_PATH = 'vectorstore/db_faiss'




embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2', model_kwargs={'device': 'cpu'})

# loader = UnstructuredFileLoader("financedata.pdf",post_processors=[clean,remove_punctuation,clean_extra_whitespace],mode="elements")
# data= loader.load()



# db = FAISS.from_documents(data, embeddings)
# db.save_local(DB_FAISS_PATH)


db = FAISS.load_local(DB_FAISS_PATH, embeddings,allow_dangerous_deserialization=True)


check_finance_prompt ="""You are a helpful Financial assistant and  has a decade of experience, you are an agent capable of determining whether the information belong to finance sector or not.
                         We have provided you with the data related to finance 101 which contains basic information about stocks, mutual funds and other some basic stuff related to it.
                         so now your job is tell if the user is asking a question related to this information you have or something else.
                         Also if the user is asking about something like calculate interest and provided some values then also i suggest you return False to such questions.
                         Remember when user is asking info about specific stock info provided symbol and timeperiod you do not have that info we have seperate function for it. you only have info about general information on background of finance.
                         Also if user is asking some questions related to math and asking to solve you do not have that info as well. so repond with provided structure with result false
                         You must respond only the json strucutre output in format provided below and nothing else. Do not answer Beyond the strucutre provided to you as examples.

                         example if user asks a question like "what is capital of france?" you must respond with json output:
                         ```json
                         {
                         "toolname":"Check",
                         "result": "false"
                         }
                         ```

                         or for question like "what are mutual funds" since you have this info in your documents you must respond with json format output like this:

                         ```json
                         {
                         "toolname":"Check",                         
                         "result": "true"
                         }
                         ```

                         but if user asks a question about calculating interest like "what is the interest for capital of 1000 and rate of 5%  and period of 6years and debit of 2 years" something like you must respond like this:

                        ```json
                         {
                         "toolname":"Check",
                         "result": "false"
                         }
                         ```
                         but if user asks a question about some math like "evaluate x+3+2x when x is 1" or any math related  something like you must respond like this:

                        ```json
                         {
                         "toolname":"Check",
                         "result": "false"
                         }
                         ```


                         but if user asks a question about information about a stock and asking info about it  like "What is the stock price of symbol CCL from jan 2023 to may 2023" something like you must respond like this:

                        ```json
                         {
                         "toolname":"Check",
                         "result": "false"
                         }
                         ```
                        but if user asks a question about information about a stock and provided a symbol and a starting date and asking info about it  like "What is the stock price of symbol CCL for last 5 months" something like you must respond like this:

                        ```json
                         {
                         "toolname":"Check",
                         "result": "false"
                         }
                         ```
                         but if user asks a question about information about a question that related to or that need the user informations "Can you show me how much I have saved personally over the last year so I can understand how much I can invest?" something like you must respond like this:

                        ```json
                         {
                         "toolname":"Check",
                         "result": "false"
                         }
                         ```
"""




def get_answer_with_ai_public(query):
    query=entranslator.translate(query)

    res = generate_text(query,check_finance_prompt)
    # print(res)
    action_dict = format_output(res)
    if action_dict['result']=="true":
        docs = db.similarity_search(query,k=3)
        # print(docs)
        data = "\n".join([doc.page_content for doc in docs])
        sources="<br>".join([doc.metadata['source']+"  page number:"+ str(doc.metadata["page_number"]) for doc in docs])

        message=f""" Data: {data}
        Based on the given data above can you answer {query}
        """
        # print("Message:",message)

        response= get_answer(message)
        if response['rtype']=='text':
            response['result']= ittranslator.translate(response['result'])
        return response
    else:
        response=get_answer(query)
        if response['rtype']=='text':
            response['result']= ittranslator.translate(response['result'])
        return response







