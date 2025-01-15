from langchain_openai import ChatOpenAI

llm: ChatOpenAI = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    temperature=0,
    api_key="not-needed",
    model="llama-3.2-1b-instruct"
)

def get_llm():
    return llm
