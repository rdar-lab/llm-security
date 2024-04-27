import logging

from django.conf import settings
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, AzureChatOpenAI

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
        elif self.__llm_type == "azure_openai":
            self.__llm_endpoint = settings.LLM_ENDPOINT
            self.__llm_api_version = settings.LLM_API_VERSION
            self.__llm_deployment_name = settings.LLM_DEPLOYMENT_NAME
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
    def __run_in_chain(model, instruction_template, input_variables):
        _logger.info(f"Running in LLM chain: {instruction_template}. Variables={input_variables}")
        prompt = PromptTemplate.from_template(instruction_template)
        chain = prompt | model
        answer = chain.invoke(input_variables)
        _logger.info(f"Answer: {answer}")
        return answer

    def answer_question_on_db(self, instruction_template, input_variables):
        agent = create_sql_agent(self.__llm, db=self.__db, verbose=True,
                                 agent_executor_kwargs={"return_intermediate_steps": True})
        return self.__run_in_chain(agent, instruction_template, input_variables)

    def answer_question(self, instruction_template, input_variables):
        return self.__run_in_chain(self.__llm, instruction_template, input_variables)


if __name__ == '__main__':
    import os
    from django.core.wsgi import get_wsgi_application

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llm_project.settings')
    application = get_wsgi_application()
    from langchain.globals import set_debug

    set_debug(False)
    llm_helper = LLmHelper()
    response = llm_helper.answer_question('You are a math expert. Answer the equation specified. {query}',
                                          {'query': '100*5='})
    print(response)
