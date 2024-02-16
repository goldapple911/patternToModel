from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'uploaded-files', views.UploadedFileViewSet, basename='uploaded-file')

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_file, name='upload_file'),
    path('upload_success/', views.upload_success, name='upload_success'),
    path('api/', include(router.urls)),
]

# curl -X POST -H "Content-Type: multipart/form-data" \
#   -F "title=title1" \
#   -F "image=@/home/code/Documents/Projects/patternToModel/source_file/source/pattern.png" \
#   -F "file_3d=@/home/code/Documents/Projects/patternToModel/source_file/source/cylinder.glb" \
#   http://127.0.0.1:8000/api/uploaded-files/