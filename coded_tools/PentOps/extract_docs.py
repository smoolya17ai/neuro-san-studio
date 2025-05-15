
# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# nsflow SDK Software in commercial settings.
#
# END COPYRIGHT
from typing import Any, Dict, Union
import os
from PyPDF2 import PdfReader
from neuro_san.interfaces.coded_tool import CodedTool


class ExtractDocs(CodedTool):
    """
    CodedTool implementation extracts text from all PDFs in the given directory. 
    Returns a dictionary mapping each PDF file name to its extracted text.
    """
    def __init__(self):
        self.default_path = ["coded_tools/PentOps/policydocs/"]
        self.docs_path = {
            "JP 3-0": "coded_tools/PentOps/policydocs/jp3_0",
            "JP 3-0appd": "coded_tools/PentOps/policydocs/jp3_0appd",
            "JP 3-04": "coded_tools/PentOps/policydocs/jp3_04",
            "JP 3-08": "coded_tools/PentOps/policydocs/jp3_08",
            "JP 3-11": "coded_tools/PentOps/policydocs/jp3_11",
            "JP 3-12": "coded_tools/PentOps/policydocs/jp3_12",
            "JP 3-13-4": "coded_tools/PentOps/policydocs/jp3_13_4",
            "JP 3-14": "coded_tools/PentOps/policydocs/jp3_14",
            "JP 3-24": "coded_tools/PentOps/policydocs/jp3_24",
            "JP 3-36": "coded_tools/PentOps/policydocs/jp3_36",
            "JP 3-53": "coded_tools/PentOps/policydocs/jp3_53",
            "JP 3-57": "coded_tools/PentOps/policydocs/jp3_57",
            "JP 3-60": "coded_tools/PentOps/policydocs/jp3_60",
            "JP 3-61": "coded_tools/PentOps/policydocs/jp3_61",
            "JP 3-85": "coded_tools/PentOps/policydocs/jp3_85",
            "JP 5-0ch1": "coded_tools/PentOps/policydocs/jp5_0ch1",
            "JP 335sig-v2": "coded_tools/PentOps/policydocs/jp335sig_v2"
        }

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        :param args: An argument dictionary with the following keys:
            - "directory" (str): The directory containing the documents.

        :param sly_data: A dictionary whose keys are defined by the agent hierarchy,
            but whose values are meant to be kept out of the chat stream.

            This dictionary is largely to be treated as read-only.
            It is possible to add key/value pairs to this dict that do not
            yet exist as a bulletin board, as long as the responsibility
            for which coded_tool publishes new entries is well understood
            by the agent chain implementation and the coded_tool implementation
            adding the data is not invoke()-ed more than once.

            Keys expected for this implementation are:
                None

        :return:
            If successful:
                A dictionary containing extracted text with the keys:
                - "file_name": The path and name of the processed document file.
                - "text": The extracted text from the document.
            Otherwise:
                A text string error message in the format:
                "Error: <error message>"
        """
        app_name: str = args.get("doc_name", None)
        print("############### PDF text reader ###############")
        print(f"Doc name: {app_name}")
        if app_name is None:
            return "Error: No app name provided."
        directory = self.docs_path.get(app_name, self.default_path)

        if not isinstance(directory, (str, bytes, os.PathLike)):
            raise TypeError(f"Expected str, bytes, or os.PathLike object, got {type(directory).__name__} instead")
        
        docs = {}
        for root, dirs, files in os.walk(directory):
            for file in files:
                # Build the full path to the file
                file_path = os.path.join(root, file)
                
                if file.lower().endswith(".pdf"):
                    # Extract PDF content
                    content = self.extract_pdf_content(file_path)
                    # Store in the dictionary using a relative path (relative to the main directory)
                    rel_path = os.path.relpath(file_path, directory)
                    docs[rel_path] = content
                elif file.lower().endswith(".txt"):
                    # Extract text file content
                    content = self.extract_txt_content(file_path)
                    # Store in the dictionary using a relative path
                    rel_path = os.path.relpath(file_path, directory)
                    docs[rel_path] = content
        print("############### Documents extraction done ###############")
        if not docs:
            print("No PDF or text files found in the directory.")
            return {"docs": {}}
        return {"files": docs}

    def extract_pdf_content(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file using PyPDF2, while attempting to preserve
        pagination (by inserting page headers).
        
        :param pdf_path: Full path to the PDF file.
        :return: Extracted text from the PDF.
        """
        text_output = []
        try:
            reader = PdfReader(pdf_path)
            for page_num, page in enumerate(reader.pages):
                # Add a page header for pagination
                text_output.append(f"\n\n--- Page {page_num + 1} ---\n\n")
                # Extract text from the page (fall back to empty string if None)
                page_text = page.extract_text() or ""
                text_output.append(page_text)
        except Exception as e:
            # In case there's an issue with reading the PDF
            print(f"Error reading PDF {pdf_path}: {e}")
            return ""

        return "".join(text_output)

    def extract_txt_content(self, txt_path: str) -> str:
        """
        Extract text from a plain text file.
        
        :param txt_path: Full path to the TXT file.
        :return: Content of the text file.
        """
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            # In case there's an issue with reading the text file
            print(f"Error reading TXT {txt_path}: {e}")
            return ""
