from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.utilities import ArxivAPIWrapper
from langchain_community.tools import ArxivQueryRun
from langchain.agents import AgentExecutor
from langchain.agents import create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain import hub
import os
from dotenv import load_dotenv
import gradio as gr
from langchain.tools.retriever import create_retriever_tool

load_dotenv()

api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1000)

wiki = WikipediaQueryRun(api_wrapper=api_wrapper)

os.environ['OPENAI_API_KEY'] = 'sk-proj-IomrCetlMNSg4Qu6FFFaT3BlbkFJk4MEgZFhi2lFIOQVsljt'

loader = WebBaseLoader("https://indianexpress.com/")

#load data into Faiss DB with Embedded
docs = loader.load()

documents = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=1000).split_documents(docs)
vectordb = FAISS.from_documents(documents, OpenAIEmbeddings())

# retriver

retriever = vectordb.as_retriever()

retriever_tool = create_retriever_tool(retriever, "Company_Agent", "Search for information about Company. For any questions about Company, you must use this tool!")

arxiv_wrapper = ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=1000)
arxiv = ArxivQueryRun(api_wrapper=arxiv_wrapper)

#Agent multiple
tools = [wiki, arxiv, retriever_tool]

llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
prompt = hub.pull("hwchase17/openai-functions-agent")

agent = create_openai_tools_agent(llm, tools, prompt)

##agentExecutor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def agent_response(query,context=None):
    response = agent_executor.invoke({"input": query})

    return response.get('output')

# Clear chat function
def clear_chat():
    return ""

# Gradio chat interface
chat_iface = gr.ChatInterface(
    fn=agent_response,
    title="Chat with AI Agent",
    clear_btn="Clear"
)
chat_iface.launch(share=True)

