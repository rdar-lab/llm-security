from django.urls import path

from .views import AskQuestionOnSiteReactView, AskQuestionOnSiteWithDataView

urlpatterns = [
    path('ask-with-data/', AskQuestionOnSiteWithDataView.as_view(), name='site_question_data'),
    path('ask-with-react/', AskQuestionOnSiteReactView.as_view(), name='site_question_react'),
]
