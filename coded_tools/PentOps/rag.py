
"""Tool module for doing RAG from a pdf file"""

# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san SDK Software in commercial settings.
#
# END COPYRIGHT

import os
from typing import Any
from typing import Dict
from typing import List

from langchain_community.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_core.vectorstores.base import VectorStoreRetriever
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from neuro_san.interfaces.coded_tool import CodedTool


class RAG(CodedTool):
    """
    CodedTool implementation which provides a way to do RAG on a pdf file
    """

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]):
        """
        :param args: An argument dictionary whose keys are the parameters
            to the coded tool and whose values are the values passed for
            them by the calling agent.  This dictionary is to be treated as
            read-only.

        :param sly_data: A dictionary whose keys are defined by the agent
            hierarchy, but whose values are meant to be kept out of the
            chat stream.

            This dictionary is largely to be treated as read-only.
            It is possible to add key/value pairs to this dict that do not
            yet exist as a bulletin board, as long as the responsibility
            for which coded_tool publishes new entries is well understood
            by the agent chain implementation and the coded_tool
            implementation adding the data is not invoke()-ed more than
            once.
        """

    async def async_invoke(
            self,
            args: Dict[str, Any],
            sly_data: Dict[str, Any]
    ) -> str:
        """
        Load a PDF from URL, build a vector store, and run a query against it.

        :param args: Dictionary containing 'query' (search string)
        :param sly_data: A dictionary whose keys are defined by the agent
            hierarchy, but whose values are meant to be kept out of the
            chat stream.

            This dictionary is largely to be treated as read-only.
            It is possible to add key/value pairs to this dict that do not
            yet exist as a bulletin board, as long as the responsibility
            for which coded_tool publishes new entries is well understood
            by the agent chain implementation and the coded_tool implementation
            adding the data is not invoke()-ed more than once.

            Keys expected for this implementation are:
                None
        :return: Text result from querying the built vector store,
            or error message
        """
        # Extract arguments from the input dictionary
        dockey: str = args.get("document_name", "")

        # Validate presence of required inputs
        if not dockey:
            return "Error: No document_name provided."

        # Extract arguments from the input dictionary
        query: str = args.get("query", "")

        # Validate presence of required inputs
        if not query:
            return "Error: No query provided."

        vectorstore: InMemoryVectorStore = await self.generate_vectorstore(dockey)
        return await self.query_vectorstore(vectorstore, query)

    async def generate_vectorstore(
            self,
            doc_key: str = None
    ) -> InMemoryVectorStore:
        """
        Asynchronously loads a specific PDF document based on its key in the documents dictionary,
        splits it into chunks, and builds an in-memory vector store using OpenAI embeddings.

        :param doc_key: Key of the document to load from the document dictionary
        :return: In-memory vector store containing the embedded document chunks
        """
        # Define the document dictionary mapping document names to file paths
        doc_dict = {
            "JP 3-0": "coded_tools/PentOps/policydocs/jp3_0/jp3_0.pdf",
            "JP 3-0appd": "coded_tools/PentOps/policydocs/jp3_0appd/jp3_0appd.pdf",
            "JP 3-04": "coded_tools/PentOps/policydocs/jp3_04/jp3_04.pdf",
            "JP 3-08": "coded_tools/PentOps/policydocs/jp3_08/jp3_08.pdf",
            "JP 3-11": "coded_tools/PentOps/policydocs/jp3_11/jp3_11.pdf",
            "JP 3-12": "coded_tools/PentOps/policydocs/jp3_12/jp3_12.pdf",
            "JP 3-13-4": "coded_tools/PentOps/policydocs/jp3_13_4/jp3_13_4.pdf",
            "JP 3-14": "coded_tools/PentOps/policydocs/jp3_14/jp3_14.pdf",
            "JP 3-24": "coded_tools/PentOps/policydocs/jp3_24/jp3_24.pdf",
            "JP 3-36": "coded_tools/PentOps/policydocs/jp3_36/jp3_36.pdf",
            "JP 3-53": "coded_tools/PentOps/policydocs/jp3_53/jp3_53.pdf",
            "JP 3-57": "coded_tools/PentOps/policydocs/jp3_57/jp3_57.pdf",
            "JP 3-60": "coded_tools/PentOps/policydocs/jp3_60/jp3_60.pdf",
            "JP 3-61": "coded_tools/PentOps/policydocs/jp3_61/jp3_61.pdf",
            "JP 3-85": "coded_tools/PentOps/policydocs/jp3_85/jp3_85.pdf",
            "JP 5-0ch1": "coded_tools/PentOps/policydocs/jp5_0ch1/jp5_0ch1.pdf",
            "JP 335sig-v2": "coded_tools/PentOps/policydocs/jp335sig_v2/jp335sig_v2.pdf"
        }

        # Validate and load the requested document
        if doc_key not in doc_dict:
            raise ValueError(f"Document key '{doc_key}' not found in available documents")

        file_path = doc_dict[doc_key]

        # Derive vector store path
        relative_path = file_path.replace("policydocs", "vector_store")
        vector_store_path = os.path.splitext(relative_path)[0] + ".json"

        try:
            vectorstore = InMemoryVectorStore.load(
                path=vector_store_path,
                embedding=OpenAIEmbeddings()
            )
            print(f"Loaded vector store from: {vector_store_path}")
            return vectorstore
        except FileNotFoundError:
            print(f"Vector store not found. Creating from PDF: {file_path}")

        # Initialize an empty list to store all documents
        all_docs = []
        reader = PdfReader(file_path)
        for page_number, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                if text and text.strip():  # Skip empty pages
                    all_docs.append(Document(
                        page_content=text,
                        metadata={"source": file_path, "page": page_number}
                    ))
                else:
                    print(f"⚠️ Empty or image-only page {page_number + 1}, skipped.")
            except IndexError as index_error:
                print(f"❌ Error extracting page {page_number + 1}: {index_error}")

        # Split documents into smaller chunks for better embedding and retrieval
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=100, chunk_overlap=50
        )
        doc_chunks: List[Document] = text_splitter.split_documents(all_docs)

        # Create an in-memory vector store with embeddings
        vectorstore: InMemoryVectorStore = await InMemoryVectorStore.afrom_documents(
            documents=doc_chunks,
            collection_name="rag-in-memory",
            embedding=OpenAIEmbeddings(),
        )
        os.makedirs(os.path.dirname(vector_store_path), exist_ok=True)
        vectorstore.dump(path=vector_store_path)
        print(f"Vector store saved to: {vector_store_path}")

        return vectorstore

    async def query_vectorstore(
            self, vectorstore: InMemoryVectorStore,
            query: str
    ) -> str:
        """
        Query the given vector store using the provided query string
        and return the combined content of retrieved documents.

        :param vectorstore: The in-memory vector store to query
        :param query: The user query to search for relevant documents
        :return: Concatenated text content of the retrieved documents
        """
        # Create a retriever interface from the vector store
        retriever: VectorStoreRetriever = vectorstore.as_retriever()

        # Perform an asynchronous similarity search
        results: List[Document] = await retriever.ainvoke(query)

        # Concatenate the content of all retrieved documents
        return "\n\n".join(doc.page_content for doc in results)
