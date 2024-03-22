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
from model import *
from utils import *
ittranslator= GoogleTranslator(source='en', target='it')
entranslator= GoogleTranslator(source='it', target='en')
# Define the path for generated embeddings
DB_FAISS_PATH = 'vectorstore/db_faiss'




embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2', model_kwargs={'device': 'cpu'})

# loader = UnstructuredFileLoader("financedata.pdf",post_processors=[clean,remove_punctuation,clean_extra_whitespace])
# data= loader.load()



# db = FAISS.from_documents(data, embeddings)
# db.save_local(DB_FAISS_PATH)


db = FAISS.load_local(DB_FAISS_PATH, embeddings,allow_dangerous_deserialization=True)

def get_answer_with_ai_public(query):
    query=entranslator.translate(query)


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



