from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from homeapp import user
import json

# Create your views here.
def main(request):
    return render(request,"mainapp/main2.html")
    # return HttpResponse("mainpage")