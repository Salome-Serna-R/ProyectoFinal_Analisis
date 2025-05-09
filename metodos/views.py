from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'home.html')

def capitulo1(request):
    return render(request, 'capitulo1.html')

def capitulo2(request):
    return render(request, 'capitulo2.html')

def capitulo3(request):
    return render(request, 'capitulo3.html')

def capitulo4(request):
    return render(request, 'capitulo4.html')
