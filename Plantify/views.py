from django.shortcuts import render
import requests
import openai
import torch
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from transformers import AutoModelForImageClassification, AutoImageProcessor, ViTImageProcessor
from PIL import Image
from .forms import UploadImageForm
from .models import Plants

def get_pred(img):
    repo_name = 'purabp1249/swin-tiny-patch4-window7-224-finetuned-herbify'
    image_processor = AutoImageProcessor.from_pretrained(repo_name)
    model = AutoModelForImageClassification.from_pretrained(repo_name)  

    try:
        with Image.open(img) as image2:
        # Do something with the image, for example, display it
            image2.show()
    except IOError:
        print("Unable to load image")
    encoding = image_processor(image2.convert("RGB"), return_tensors="pt")
    print(encoding.pixel_values.shape)
    with torch.no_grad():
        outputs = model(**encoding)
        logits = outputs.logits
    predicted_class_idx = logits.argmax(-1).item()
    print(model.config.id2label[predicted_class_idx])
    return model.config.id2label[predicted_class_idx]


def get_api_data(request,var):
        url = 'https://trefle.io/api/v1/plants/search?token=yL5wSdz-_-R3WEnwH7AFamGjlOo3Aof3TXboad0OyeY&q='+var  # Corrected URL
        response = requests.get(url)

        openai.api_key = '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'
        common_name=var
        # if response.status_code == 200:
        #     # Now, json_data contains the JSON response from the API
        json_data = response.json()
        #     common_name=json_data['common_name']
            # if 'common_name' in json_data:
            #     name = json_data['common_name']
            # else:
            #     name=json_data['scientific_name']

        AIresponse1 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "assistant", "content":"List the places where we can find "+ common_name + " plant in 50 words in India."},
            ]
        )

        AIresponse2 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "assistant", "content": "What are the medicinal Uses of" + common_name +"in 50 words in points?"},
            ]
        )

        c1=AIresponse1.choices[0]['message']['content']
        c2=AIresponse2.choices[0]['message']['content']

        # Loop through the list of plants in the "data" key
        for plant in json_data['data']:
                id = plant['id']
                common_name = plant['common_name']
                scientific_name = plant['scientific_name']
                image_url = plant['image_url']
                year = plant['year']  # Extract the 'year' value
                family = plant['family']  # Extract the 'family' value
                params = {'image':'/static/photo/t3.jpg','id':id,'common_name': common_name,'scientific_name':scientific_name,'image_url':image_url,'year':year,'family':family,'AIresponse1':c1,'AIresponse2':c2}
                return(params)

def home(request):
    params={'image':'static/photo/kuch.jpg'}
    return render(request, 'home.html',params)

def plant(request):
        if request.method == 'POST':
            image=request.FILES['photo']
            pred=get_pred(image)
            params=get_api_data(request,pred)
            return render(request,'plant.html',params)
        my_list=[1,2,3,4,5]
        params={'my_list':my_list}
        return render(request,'list.html',params)

def about(request):
    params={'image':'static/photo/t3.jpg'}
    return render(request, 'about us.html',params)

def db_connect():
    from pymongo.mongo_client import MongoClient
    from pymongo.server_api import ServerApi
    uri = "mongodb+srv://Plantify:<password>@plantify1.ejfx540.mongodb.net/?retryWrites=true&w=majority"
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)