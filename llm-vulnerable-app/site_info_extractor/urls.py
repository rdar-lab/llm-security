from django.urls import path

from .views import AskQuestionOnSiteView

urlpatterns = [
    path('ask/', AskQuestionOnSiteView.as_view(), name='site_question'),
]
