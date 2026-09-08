from django.http import HttpResponse


def home(request):
    return HttpResponse("Family Chore Tracker")
