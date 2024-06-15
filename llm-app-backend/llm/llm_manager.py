import logging
from abc import ABC
from typing import Optional

import tiktoken
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

from llm.protectors.protector import LLMProtector
from llm.utils import website_reader, reader_tool

_MAX_TOKENS = 7000
_MAX_CHARS = _MAX_TOKENS * 4

_logger = logging.getLogger(__name__)


class LLMManager(ABC):
    __db_url = None

    def __init__(self, protector: Optional[LLMProtector] = None):
        super().__init__()
        self._init_llm()
        self.__db = None
        self.__protector = protector
        self.__tokenization_encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")

    def __get_db(self):
        if self.__db is None:
            if LLMManager.__db_url is None:
                LLMManager.__db_url = self.__calc_db_url()
            self.__db = SQLDatabase.from_uri(LLMManager.__db_url)
        return self.__db

    @staticmethod
    def __calc_db_url():
        engine = settings.DATABASES['default']['ENGINE']
        name = settings.DATABASES['default']['NAME']
        if 'sqlite' in engine:
            _logger.info("Using SQLite database")
            _logger.info(f"Using URL=" + f"sqlite:////{name}")
            db_url = f"sqlite:////{name}"
        elif 'postgresql' in engine:
            _logger.info("Using PostgreSQL database")
            user = settings.DATABASES['default']['USER']
            password = settings.DATABASES['default']['PASSWORD']
            host = settings.DATABASES['default']['HOST']
            port = settings.DATABASES['default']['PORT']
            _logger.info(f"Using URL=" + f"postgresql://{user}:XXX@{host}:{port}/{name}")
            db_url = f"postgresql://{user}:{password}@{host}:{port}/{name}"
        else:
            raise ValueError('Unsupported database engine')
        return db_url

    def _init_llm(self):
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
            return LLMManager.parse_answer(answer.content)

        if isinstance(answer, dict) and "output" in answer:
            return LLMManager.parse_answer(answer["output"])

        if isinstance(answer, dict) and "answer" in answer:
            return LLMManager.parse_answer(answer["answer"])

        return str(answer)

    @staticmethod
    def __is_template(instruction):
        return '{' in instruction

    @staticmethod
    def __calc_instruction_template(instruction, input_variables):
        if 'query' in input_variables:
            if LLMManager.__is_template(instruction):
                instruction = PromptTemplate.from_template(instruction).format(**input_variables)

            input_variables = {**input_variables, 'instruction': instruction}
            if 'data' in input_variables:
                instruction = '{instruction}\nHere is the data:\n{data}\nAnswer the question below:\n{query}'
            else:
                instruction = '{instruction}\nAnswer the question below:\n{query}'

        return instruction, input_variables

    def __run_llm(self, model, app_instruction, user_input_variables, wrap_prompt=False):
        _logger.info(f"Running in LLM: {app_instruction}. Variables={user_input_variables}")

        system_instruction_template, system_input_variables = \
            self.__calc_instruction_template(app_instruction, user_input_variables)
        if self.__protector is not None:
            system_instruction_template, system_input_variables = self.__protector.protect_call(
                system_instruction_template, system_input_variables, app_instruction, user_input_variables)

        prompt = PromptTemplate.from_template(system_instruction_template).format(**system_input_variables)

        _logger.info(f"Prompt: {prompt}")

        if wrap_prompt:
            prompt = {"input": prompt}
        answer = model.invoke(prompt)
        _logger.info(f"Answer: {answer}")
        return answer

    def answer_question_on_db_with_rag(self, instruction_template, input_variables):
        agent = create_sql_agent(self.__llm, db=self.__get_db(), verbose=True,
                                 agent_executor_kwargs={"return_intermediate_steps": True})
        return self.__run_llm(agent, instruction_template, input_variables)

    def answer_question(self, instruction_template, input_variables):
        return self.__run_llm(self.__llm, instruction_template, input_variables)

    def answer_question_on_web_page_with_retriever(self, instruction_template, input_variables, embedding=True):
        documents = website_reader.read_from_url(input_variables['url'])
        return self.__answer_question_on_documents(documents, instruction_template, input_variables,
                                                   embedding=embedding)

    def answer_question_on_web_page_with_rag(self, instruction_template, input_variables):
        return self.__answer_question_with_tools(
            [reader_tool.SimpleReaderTool(), reader_tool.ReaderTool()],
            instruction_template,
            input_variables
        )

    def __chain_for_retriever(self, documents):
        if len(documents) == 0 or (len(documents) == 1 and documents[0].page_content == ""):
            raise Exception("No content found in the document")
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        db = FAISS.from_documents(texts, self.__embedding)
        retriever = db.as_retriever()
        chain = RetrievalQAWithSourcesChain.from_chain_type(llm=self.__llm, chain_type="stuff", retriever=retriever,
                                                            reduce_k_below_max_tokens=True,
                                                            max_tokens_limit=_MAX_TOKENS)
        return chain

    def __answer_question_on_documents(self, documents, instruction_template, input_variables, embedding=True):
        if embedding:
            chain = self.__chain_for_retriever(documents)

            return self.__run_llm(chain, instruction_template, input_variables)
        else:
            page_content = "\n".join([doc.page_content for doc in documents])
            if len(page_content) > _MAX_CHARS:
                _logger.warning(f"Page content is too long. Truncating to {_MAX_CHARS} chars")
                page_content = page_content[:_MAX_CHARS]
            return self.answer_question(instruction_template, {**input_variables, "data": page_content})

    def __answer_question_with_tools(self, tools, instruction_template, input_variables):
        prompt = hub.pull("hwchase17/structured-chat-agent")
        agent = create_structured_chat_agent(
            self.__llm,
            tools,
            prompt=prompt,
        )
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        agent_executor.return_intermediate_steps = True
        return self.__run_llm(agent_executor, instruction_template, input_variables, wrap_prompt=True)

    def tokenize(self, text):
        return self.__tokenization_encoder.encode(text)

    def detokenize(self, tokens):
        return self.__tokenization_encoder.decode(tokens)
