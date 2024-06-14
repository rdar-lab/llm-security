from django.urls import path

from .views import AskQuestionOnSiteRagView, AskQuestionOnSiteRetrieverView

urlpatterns = [
    path('ask-with-retriever/', AskQuestionOnSiteRetrieverView.as_view(), name='site_question_retriever'),
    path('ask-with-rag/', AskQuestionOnSiteRagView.as_view(), name='site_question_rag'),
]
