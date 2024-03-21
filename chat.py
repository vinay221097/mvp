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
translator= GoogleTranslator(source='en', target='it')
# Define the path for generated embeddings
DB_FAISS_PATH = 'vectorstore/db_faiss'
import os

llm = ChatOpenAI(
    model_name="TheBloke_Mixtral-8x7B-Instruct-v0.1-GPTQ",
    openai_api_key=os.getenv("OPENAI_KEY",None),
    openai_api_base="https://4d4z2mnsfrjdt8-5000.proxy.runpod.net/v1/"
)


embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2', model_kwargs={'device': 'cpu'})

# loader = UnstructuredFileLoader("financedata.pdf",post_processors=[clean,remove_punctuation,clean_extra_whitespace], mode='elements')
# data= loader.load()



# db = FAISS.from_documents(data, embeddings)
# db.save_local(DB_FAISS_PATH)


db = FAISS.load_local(DB_FAISS_PATH, embeddings,allow_dangerous_deserialization=True)

def get_answer_with_ai_public(query):


    docs = db.similarity_search(query,k=3)
    # print(docs)
    data = "\n".join([doc.page_content for doc in docs])
    sources="<br>".join([doc.metadata['source'] for doc in docs])

    messages = [
            SystemMessage(
                content=f"""You are a Financial analyst and have a decade of experience is good at analyzing the data and good at understanding the user queries and answering them based on your knowledge and information provided to you.
                 If you do not know the answer reply with exact words "I do not know".              
                Data: {data}


                """
            ),
            HumanMessage(
                content=query
            ),
        ]
    response = llm.invoke(messages).content
    if sources is not None and type(sources)==str:
        response=response+sources
    return response,""


res=get_answer_with_ai_public("can you give me list of different mutual funds?")[0]
tres =  translator.translate(res)
print(tres)