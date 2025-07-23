import os
import pickle
import openai
from dotenv import load_dotenv

# Chain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import PGVector
# from langchain_community.embeddings import OpenAIEmbeddings
from langchain_core.runnables import Runnable
# from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.text_splitter import MarkdownTextSplitter
# from langchain_community.document_loaders import PyMuPDFLoader
from langchain.schema import Document


# 환경설정
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
embeddings = OpenAIEmbeddings()

# def sparse_retriever_save(pkl_name: str, pdf_path: str):
#     # 예시로 문서 객체 생성
#     documents = chunking(pdf_path)
#     document_objects = [Document(page_content=doc) for doc in documents]
#     # BM25Retriever 초기화
#     sparse_retriever = BM25Retriever.from_documents(document_objects)
 
#     # 객체를 파일로 저장
#     with open(f'bm25_db/{pkl_name}.pkl', 'wb') as file:
#         pickle.dump(sparse_retriever, file)

#     print(f"BM25Retriever 객체가 {pkl_name}.pkl 파일에 저장되었습니다.")

# def sparse_retriever_load(pkl_name: str):
#     with open(f'bm25_db/{pkl_name}.pkl', 'rb') as file:
#         sparse_retriever = pickle.load(file)
#     return sparse_retriever 
    
def retriever():
    # PGVector에 연결
    vectorstore = PGVector(
        connection_string=os.getenv('DATABASE_URL'),
        embedding_function=embeddings,
        collection_name="documents",
    )

    # Retriever 구성
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

    return retriever

# invoke 메서드 사용
# docs = retriever.invoke("건설 사고 예방 방법")
# for doc in docs:
#     print(doc.page_content)

    
# if __name__ == '__main__':
#     sparse_retriever_save('bm25_evaluation_retriever', '회사기준_pdf')