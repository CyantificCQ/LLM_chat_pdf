from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains.question_answering import load_qa_chain 
from langchain.llms.openai import OpenAI
from langchain.chains import ConversationalRetrievalChain
import openai
import glob
import os
import sys



class Chatbot:


    def __init__(self,
                env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(""))) + "\\Secret" + "\\.env" )):
        
        self.env_path = env_path
        

    def get_path(self):
        directory = "pdf_files"
        filetype = "*.pdf"
        path = glob.glob(os.path.join(directory + "/" + filetype))
        files = [f for f in os.listdir(directory) if f.endswith(filetype[1:])]
        return path, files
    

    def read_pdfs(self):
        path,_ = self.get_path()
        if path is not None:
            text = ""
            for pdfs in path:
                    pdf_reader = PdfReader(pdfs)
                    for pages in pdf_reader.pages:
                        text += pages.extract_text()
            return text
        else:
            return "There is no pdf file uploaded"
    
    def get_chunks(self):
        text = self.read_pdfs()
        text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap = 200,
        length_function=len)
        chunks = text_splitter.split_text(text)
        return chunks
    
   
    def get_chain(self):
        load_dotenv(dotenv_path=self.env_path)
        openai.api_key = os.getenv("OPENAI_API_KEY")
        embeddings = OpenAIEmbeddings()
        vector_store = FAISS.from_texts(texts=self.get_chunks(), embedding=embeddings)

        client = ChatOpenAI(model_name="gpt-3.5-turbo-1106")
        memory = ConversationBufferMemory(memory_key = "chat_history", return_message=True)
        chain = ConversationalRetrievalChain.from_llm(
            llm=client,
            retriever=vector_store.as_retriever(),
            memory = memory
        )
        
        return chain


            


# if __name__ == "__main__":
#     llm_chat = Chatbot()
#     while True:
#         query = input("User:")
#         if query.lower() in ["break", "quit", "q", "close", "enough"]:
#             break
#         chain = llm_chat.get_chain()
#         response = chain.run(question=query)
#         print({"AI":response})


