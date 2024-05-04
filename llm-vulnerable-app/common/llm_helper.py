import logging

from django.conf import settings
from langchain import hub
from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.vectorstores import FAISS
from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter

from common import website_reader, reader_tool

_MAX_TOKENS = 7000

_logger = logging.getLogger(__name__)


class LLmHelper:
    __db_url = None

    def __init__(self):
        super().__init__()
        self.__init_llm()
        self.__init_db()

    def __init_db(self):
        if LLmHelper.__db_url is None:
            LLmHelper.__db_url = self.__calc_db_url()
        self.__db = SQLDatabase.from_uri(LLmHelper.__db_url)

    @staticmethod
    def __calc_db_url():
        engine = settings.DATABASES['default']['ENGINE']
        name = settings.DATABASES['default']['NAME']
        if 'sqlite' in engine:
            _logger.info("Using SQLite database")
            db_url = f"sqlite:////{name}"
        elif 'postgresql' in engine:
            _logger.info("Using PostgreSQL database")
            user = settings.DATABASES['default']['USER']
            password = settings.DATABASES['default']['PASSWORD']
            host = settings.DATABASES['default']['HOST']
            port = settings.DATABASES['default']['PORT']
            db_url = f"postgresql:////{user}:{password}@{host}:{port}/{name}"
        else:
            raise ValueError('Unsupported database engine')
        return db_url

    def __init_llm(self):
        self.__api_key = settings.LLM_API_KEY
        self.__llm_type = settings.LLM_TYPE

        if self.__llm_type == "openai_3_5_turbo":
            _logger.info("Using OpenAI GPT-3.5 Turbo model")
            self.__llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                api_key=self.__api_key,
                temperature=0
            )
            self.__embedding = OpenAIEmbeddings(
                api_key=self.__api_key
            )
        elif self.__llm_type == "azure_openai":
            self.__llm_endpoint = settings.LLM_ENDPOINT
            self.__llm_api_version = settings.LLM_API_VERSION
            self.__llm_deployment_name = settings.LLM_DEPLOYMENT_NAME
            self.__llm_embedding_deployment_name = settings.LLM_EMBEDDING_DEPLOYMENT_NAME
            _logger.info(
                f"Using Azure OpenAI model. Endpoint: {self.__llm_endpoint}, "
                f"Deployment: {self.__llm_deployment_name}")

            self.__llm = AzureChatOpenAI(
                deployment_name=self.__llm_deployment_name,
                azure_endpoint=self.__llm_endpoint,
                api_key=self.__api_key,
                api_version=self.__llm_api_version,
                temperature=0
            )
            self.__embedding = AzureOpenAIEmbeddings(
                deployment=self.__llm_embedding_deployment_name,
                azure_endpoint=self.__llm_endpoint,
                api_key=self.__api_key,
                api_version=self.__llm_api_version,
            )
        else:
            raise ValueError('Invalid LLM_TYPE in settings.py')

    @staticmethod
    def parse_answer(answer):
        if isinstance(answer, AIMessage):
            return answer.content

        if isinstance(answer, dict) and "output" in answer:
            return answer["output"]

        return str(answer)

    @staticmethod
    def __run_llm(model, instruction_template, input_variables, wrap_prompt=False):
        _logger.info(f"Running in LLM: {instruction_template}. Variables={input_variables}")
        prompt = PromptTemplate.from_template(instruction_template).format(**input_variables)
        if wrap_prompt:
            prompt = {"input": prompt}
        answer = model.invoke(prompt)
        _logger.info(f"Answer: {answer}")
        return answer

    def answer_question_on_db(self, instruction_template, input_variables):
        agent = create_sql_agent(self.__llm, db=self.__db, verbose=True,
                                 agent_executor_kwargs={"return_intermediate_steps": True})
        return self.__run_llm(agent, instruction_template, input_variables)

    def answer_question(self, instruction_template, input_variables):
        return self.__run_llm(self.__llm, instruction_template, input_variables)

    def answer_question_on_web_page(self, instruction_template, input_variables, embedding=True):
        documents = website_reader.read_from_url(input_variables['url'])
        return self._answer_question_on_documents(documents, instruction_template, input_variables, embedding=embedding)

    def _answer_question_on_documents(self, documents, instruction_template, input_variables, embedding=True):
        if embedding:
            if len(documents) == 0 or (len(documents) == 1 and documents[0].page_content == ""):
                raise Exception("No content found in the document")

            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            texts = text_splitter.split_documents(documents)

            db = FAISS.from_documents(texts, self.__embedding)
            retriever = db.as_retriever()

            chain = RetrievalQAWithSourcesChain.from_chain_type(llm=self.__llm, chain_type="stuff", retriever=retriever,
                                                                reduce_k_below_max_tokens=True,
                                                                max_tokens_limit=_MAX_TOKENS)

            return self.__run_llm(chain, instruction_template, input_variables)
        else:
            page_content = "\n".join([doc.page_content for doc in documents])
            return self.answer_question(instruction_template, {**input_variables, "page_content": page_content})

    def _answer_question_with_tools(self, tools, instruction_template, input_variables):
        prompt = hub.pull("hwchase17/structured-chat-agent")
        agent = create_structured_chat_agent(
            self.__llm,
            tools,
            prompt=prompt,
        )
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        agent_executor.return_intermediate_steps = True
        return self.__run_llm(agent_executor, instruction_template, input_variables, wrap_prompt=True)

    def answer_question_on_web(self, instruction_template, input_variables):
        return self._answer_question_with_tools(
            [reader_tool.SimpleReaderTool(), reader_tool.ReaderTool()],
            instruction_template,
            input_variables
        )


if __name__ == '__main__':
    import os
    from django.core.wsgi import get_wsgi_application

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llm_project.settings')
    application = get_wsgi_application()

    llm_helper = LLmHelper()
    response = llm_helper.answer_question('You are a math expert. Answer the equation specified. {query}',
                                          {'query': '100*5='})
    # response = llm_helper.answer_question_on_db('You are a database expert. {query}', {'query': 'Sum the transactions'})
    # response = llm_helper.answer_question_on_web_page(
    #
    #     'You are a website reader. Answer a question about the content.\n'
    #     '{query}',
    #     {
    #         "url": "https://raw.githubusercontent.com/greshake/llm-security/main/scenarios/common/albert_einstein.md",
    #         "query": "Summarize"
    #     },
    #     embedding=True
    # )
    # response = llm_helper.answer_question_on_web(
    #
    #     'You are a website reader. Answer a question about the page.\n'
    #     'URL: {url}\n'
    #     '{query}',
    #     {
    #         "url": "https://www.imdb.com/title/tt10168312/",
    #         "query": "Summarize the plot in details. Provide 500 words at least"
    #     }
    # )

    print(response)
