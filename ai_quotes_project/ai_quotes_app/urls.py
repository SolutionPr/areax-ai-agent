from django.urls import path
from . import views

urlpatterns=[
    path('fetch_quotes/', views.FetchQuotesView.as_view(), name='fetch_quotes'),
    path('upload_doc', views.PDFPagesAPIView.as_view(), name='upload_doc'),
    path('generate_description', views.Generate_DescriptionAPIView.as_view(), name='generate_description'),

]