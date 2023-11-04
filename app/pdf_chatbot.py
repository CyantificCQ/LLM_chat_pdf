import streamlit as st 
from PyPDF2 import PdfReader 
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, user_template, bot_template
from langchain.llms.huggingface_hub import HuggingFaceHub
import requests, json
import pinecone
import os

load_dotenv()

def get_pdf_text(pdf_docs):
    text = ""
    for pdfs in pdf_docs:
        pdf_reader = PdfReader(pdfs)
        for pages in pdf_reader.pages:
            text += pages.extract_text()
    return text
            

def get_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=512,
        chunk_overlap = 200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    # embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(embedding=embeddings, texts=text_chunks)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":512})
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(memory=memory,
                                                               llm=llm,
                                                               retriever=vectorstore.as_retreiver())
 
    return conversation_chain


def handle_userinput(user_question):
    response = st.session_state.conversation({"question": user_question})
    st.session_state.chat_history = response["chat_history"]

    for i , message in enumerate(st.session_state.chat_history):
        if i % 2 ==0:
            st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)

        else:
            st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)


def main():
    st.set_page_config(page_title="Chat with your PDF files", page_icon=":robot:")
    
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    
    st.header("Chat with your PDF files 🤖")
    user_question = st.text_input("Ask a question about your documents:")
    if  user_question:
        handle_userinput(user_question)

    st.write(user_template.replace("{{MSG}}", "Hello Robot"), unsafe_allow_html=True)
    st.write(bot_template.replace("{{MSG}}", "Hello Human"), unsafe_allow_html=True)

    with st.sidebar:
        st.subheader("Your files")
        pdf_files = st.file_uploader("Upload PDFs here", accept_multiple_files=True)
        if st.button("Submit"):
            with st.spinner("Uploading and processing.."):
                raw_text = get_pdf_text(pdf_files)
                # st.write(raw_text)

                text_chunks = get_chunks(raw_text)
                # st.write(text_chunks)

                vectorstore = get_vectorstore(text_chunks=text_chunks)


                st.session_state.conversation = get_conversation_chain(vectorstore)
        


if __name__ == "__main__":
    main()