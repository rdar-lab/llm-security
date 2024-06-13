from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.views import APIView


class PingView(APIView):
    """
    Authenticate a user.
    Will simpley return 200 if the user is valid or 401 if it is not
    """
    queryset = User.objects.none()

    # noinspection PyMethodMayBeStatic
    def get(self, request):
        return JsonResponse("OK", status=200)
