from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from dataclasses import dataclass

load_dotenv()

@dataclass
class Chatbot:
    prompt: str
    pdf_files: list


    def read_pdfs(self):
        text = ""
        for pdfs in self.pdf_files:
            pdf_reader = PdfReader(pdfs)
            for pages in pdf_reader.pages:
                text += pages.extract_text()
        return text
    
    def get_chunks(self):
        text = self.read_pdfs()
        text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=512,
        chunk_overlap = 200,
        length_function=len)
        chunks = text_splitter.split_text(text)
        return chunks
    
   
    def get_vectorstore(self): 
        chunks = self.get_chunks()
        self.embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_texts(embedding=self.embeddings, texts=chunks)
        return vectorstore

