from django.shortcuts import redirect, render
from django.http import JsonResponse
import uuid
import os
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from chat.models import Chat, Session
from django.conf import settings


#importing openai libraries

import openai
from openai import OpenAI

import time

from os import listdir
from os.path import isfile, join
from pathlib import Path
import glob

session_titles = []
chats = []

my_sk = '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'
client = OpenAI(api_key=my_sk)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
mypath = str(BASE_DIR)+'/media/documents'

# Reading files to add to knowledge base (RAG)
files = []
for file in glob.glob(mypath + "/*.pdf"):
    files.append(file)

files_to_add = []
for f in files:

    file = client.files.create(
    file=open(f, "rb"),
    purpose="assistants"
    )

    files_to_add.append(file.id)


intstructions_string = "JisrBot, functioning as a virtual assistat \
, communicates in clear, accessible language, escalating \
to technical depth upon request. \
It reacts to feedback aptly and concludes with its signature '–JisrBot'. \
JisrBot will tailor the length of its responses to match the viewer's input, \
providing concise acknowledgments to brief expressions of gratitude or \
feedback, thus keeping the interaction natural and engaging."

assistant = client.beta.assistants.create(
    name="JisrBot",
    description="Virtual Assistant",
    instructions=intstructions_string,
    tools=[{"type": "file_search"}],
    tool_resources={ "code_interpreter": {"file_ids": files_to_add}},
    model="gpt-3.5-turbo"
)

def generate_uuid():
    return str(uuid.uuid4())

# Create your views here.

def home(request):
    if request.user.is_authenticated:
        return redirect('chatbot')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('chatbot')
        
    return render(request, 'login.html')



def register_user(request):
    if request.user.is_authenticated:
        return redirect('chatbot')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        if password == password2:
            user = User.objects.create_user(
                username=username,
                password=password
            )
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()

            login(request, user)
            return redirect('chatbot')
    else:
        return render(request, 'register.html')
    return render(request, 'register.html')



def user_logout(request):
    logout(request)
    return redirect('home')



@login_required(login_url='home')
def chatbot(request):
    return render(request, 'index.html')

def wait_for_assistant(thread, run):
    """
        Function to periodically check run status of AI assistant and print run time
    """

    # wait for assistant process prompt
    t0 = time.time()
    while run.status != 'completed':

        # retreive status of run (this might take a few seconds or more)
        run = client.beta.threads.runs.retrieve(
          thread_id=thread.id,
          run_id=run.id
        )

        # wait 0.5 seconds
        time.sleep(0.25)
    dt = time.time() - t0
    print("Elapsed time: " + str(dt) + " seconds")
    
    return run


def generate_chatbot_response(user_message):

    # create thread (i.e. object that handles conversation between user and assistant)
    thread = client.beta.threads.create()

    # add a user message to the thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )

    # send message to assistant to generate a response
    run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    )

    # wait for assistant process prompt
    run = wait_for_assistant(thread, run)

    # view messages added to thread
    messages = client.beta.threads.messages.list(
    thread_id=thread.id
    )

    return messages.data[0].content[0].text.value


def get_chatbot_response(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        session_titles.append(user_message)
        # chatbot_response = f'Reply from backend.\nMessage was received successfully'
        chatbot_response = generate_chatbot_response(user_message)
        chat = Chat(
            id=generate_uuid(),
            message=user_message,
            response=chatbot_response,
        )
        chats.append(chat)
        return JsonResponse({'response': chatbot_response})



@login_required(login_url='home')
def save_chat(request):
    session = Session(
        id=generate_uuid(),
        title=session_titles[0],
        user=request.user,
    )
    session.save()
    for chat in chats:
        chat.session = session
        chat.save()
    chats.clear()
    session_titles.clear()
    return redirect('chatbot')



@login_required(login_url='home')
def load_chats(request, session_id):
    session  = Session.objects.get(id=session_id)
    session_titles.clear()
    session_titles.append(session.title)

    user_chats = Chat.objects.filter(session=session)
    for chat in user_chats:
        chats.append(chat)

    return render(request, 'index.html', {
        'chats': user_chats,
        'load': True,
    })



@login_required(login_url='home')
def delete_session(request, session_id):
    session  = Session.objects.get(id=session_id)
    session.delete()
    return redirect('history', request.user.username)



@login_required(login_url='home')
def history(request, username):
    user = User.objects.get(username=username)
    sessions = Session.objects.filter(user=user)

    return render(request, 'chats.html', {
        'sessions': sessions,
    })



@login_required(login_url='home')
def new_chat(request):
    session_titles.clear()
    chats.clear()
    return redirect('chatbot')