from django.shortcuts import render

# Create your views here.

from django.views.generic import ListView, CreateView
from .models import userfiles
from django.urls import reverse_lazy
from .forms import PostForm


class HomePageView(ListView):
    model = userfiles
    template_name = "user_files.html"

class CreateFileView(CreateView):
    model = userfiles
    form_class = PostForm
    template_name = "post_file.html"
    success_url = reverse_lazy("file_upload")