from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'home.html')

def capitulo1(request):
    return render(request, 'capitulo1.html')

