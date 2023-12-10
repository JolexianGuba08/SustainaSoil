from django.shortcuts import render


# Create your views here.
def homepage(request):
    return render(request, 'dashboard_page/user-dashboard.html')
