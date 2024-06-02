from llm.llm_manager import LLMManager

if __name__ == '__main__':
    import os
    from django.core.wsgi import get_wsgi_application

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llm_project.settings')
    application = get_wsgi_application()

    llm = LLMManager()
    # response = llm.answer_question('You are a math expert. Answer the equation specified. {query}',
    #                                       {'query': '100*5='})
    # response = llm.answer_question_on_db('You are a database expert. {query}', {'query': 'Sum the transactions'})
    response = llm.answer_question_on_web_page_with_retriever(

        'You are a website reader. Answer a question about the content.'
        '{query}',
        {
            "url": "https://raw.githubusercontent.com/greshake/llm-security/main/scenarios/common/albert_einstein.md",
            "query": "Summarize"
        },
        embedding=False
    )
    # response = llm.answer_question_on_web_page_with_rag(
    #
    #     'You are a website reader. Answer a question about the page.\n'
    #     'URL: {url}\n'
    #     '{query}',
    #     {
    #         "url": "http://0.0.0.0:8000/",
    #         "query": "Tell me what this site is about"
    #     }
    # )

    print(response)
