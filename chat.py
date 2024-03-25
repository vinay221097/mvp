import warnings
warnings.filterwarnings('ignore')

from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain.chat_models import ChatOpenAI
from unstructured.cleaners.core import remove_punctuation,clean,clean_extra_whitespace
from unstructured.cleaners.core import clean_extra_whitespace
from langchain.schema import HumanMessage, SystemMessage
from deep_translator import GoogleTranslator
from model2 import *
from utils import *
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
                         Remember you must repond to user only in the structure provided above as examples.you only have to respone the json structure and nothing else no additional explanation or addition text is needed"""












def get_answer_with_ai_public(query):
    query=entranslator.translate(query)

    res = generate_text(query,check_finance_prompt)
    action_dict = format_output(res)
    if action_dict['result']=="true":
        docs = db.similarity_search(query,k=3)
        # print(docs)
        data = "\n".join([doc.page_content for doc in docs])
        sources="<br>".join([doc.metadata['source']+"  page number:"+ str(doc.metadata["page_number"]) for doc in docs])

        message=f""" Data: {data}
        Based on the given data above can you answer {query}
        """
        print("Message",message)

        response= get_answer(message)
        return ittranslator.translate(response),sources
    else:
        response=get_answer(query)
        return ittranslator.translate(response),""






