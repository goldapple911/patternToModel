import django
from django.shortcuts import render, redirect
from .forms import FileUploadForm

from rest_framework import viewsets
from rest_framework.response import Response
from .models import UploadedFile
from .serializers import UploadedFileSerializer

import random
import string
import secrets

def index(request):
    random_str = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(15))
    print(random_str)
    request.session['user_token'] = random_str
    return render(request, 'index.html')

def upload_file(request):
    if request.session.get('user_token'):
        print(request.session.get('user_token'))
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload_success')  # Create a success template or redirect
    else:
        form = FileUploadForm()
    return render(request, 'upload_form.html', {'form': form})

def upload_success(request):
    print("success upload!")
    return render(request, 'upload_success.html')

class UploadedFileViewSet(viewsets.ModelViewSet):
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer
    
    def list(self, request, *args, **kwargs):
        # Custom logic before or after fetching the data
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        # Custom logic for additional data manipulation if needed
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Custom logic before or after creating the object
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # Custom logic for additional data manipulation if needed
        return Response(serializer.data, status=201)