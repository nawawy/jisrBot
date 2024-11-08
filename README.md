# jisrBot
A chatbot using openAI and uploads documents to the knowledge base

To use this repo follow the rules below:

Clone:

git clone https://github.com/nawawy/jisrBot

Go to the folder of the repo:

cd django_chatbot-main

Build the docker container:

docker build -t jisr_app 
docker run --name jisr_bot_c1 -p 8000:8000 -d jisr_app
docker exec -it jisr_bot_c1 python manage.py migrate

Now go to http://127.0.0.1:8000/


