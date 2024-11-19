from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app.verify import authentication
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from PIL import Image
import pytesseract
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from .models import demo ,ImageModel
import requests
from urllib.parse import urlparse 
from django.core.files.base import ContentFile 
import os

analyzer = SentimentIntensityAnalyzer()


pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'


def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text.strip()

def get_sentiment_score(text):
    sentiment_scores = analyzer.polarity_scores(text)
    compound_score = sentiment_scores['compound']
    if compound_score >= 0.05:
        return 'Positive'
    elif compound_score <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'
        

def save_image_to_model(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        # Extract file name from URL
        parsed_url = urlparse(image_url)
        file_name = os.path.basename(parsed_url.path)
        if not file_name:
            file_name = 'image.jpg' 
            print("hiii",file_name) # Provide a default name if file name extraction fails
        image_model = ImageModel()
        image_model.image.save(file_name, ContentFile(response.content), save=True)


# Create your views here.
def index(request):
    # return HttpResponse("This is Home page")    
    return render(request, "index.html")

def log_in(request):
    if request.method == "POST":
        # return HttpResponse("This is Home page")  
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username = username, password = password)

        if user is not None:
            login(request, user)
            messages.success(request, "Log In Successful...!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid User...!")
            return redirect("log_in")
    # return HttpResponse("This is Home page")    
    return render(request, "log_in.html")

def register(request):
    if request.method == "POST":
        fname = request.POST['fname']
        lname = request.POST['lname']
        username = request.POST['username']
        password = request.POST['password']
        password1 = request.POST['password1']
        # print(fname, contact_no, ussername)
        verify = authentication(fname, lname, password, password1)
        if verify == "success":
            user = User.objects.create_user(username, password, password1)          #create_user
            user.first_name = fname
            user.last_name = lname
            user.save()
            messages.success(request, "Your Account has been Created.")
            return redirect("/")
            
        else:
            messages.error(request, verify)
            return redirect("register")
    # return HttpResponse("This is Home page")    
    return render(request, "register.html")


@login_required(login_url="log_in")
@cache_control(no_cache = True, must_revalidate = True, no_store = True)
def log_out(request):
    logout(request)
    messages.success(request, "Log out Successfuly...!")
    return redirect("/")

@login_required(login_url="log_in")
@cache_control(no_cache = True, must_revalidate = True, no_store = True)
def dashboard(request):
    context = {
        'fname': request.user.first_name, 
        
        }
    return render(request, "dashboard.html",context)

@login_required(login_url="log_in")
@cache_control(no_cache = True, must_revalidate = True, no_store = True)
def text_analysis(request):
    context = {
        'fname': request.user.first_name, 
        
        }
    if request.method == "POST":
        if 'text' in request.POST:
            text = request.POST['input_text']
            sentiment = get_sentiment_score(text)
            print(sentiment)
            context['text_sentiment'] = sentiment
            context['sentence'] = text
        
        else:
            input_image = request.FILES['input_image']
            save_data=demo(images=input_image)
            save_data.save()
            img = demo.objects.last()
            image_path = str(img.images.url)
            image_path = image_path.replace("/media","media")
            
        
            extracted_text = extract_text_from_image(image_path)

            if extracted_text:
                sentiment = get_sentiment_score(extracted_text)
                context['post_sentiment'] = sentiment
                context['sentence'] = extracted_text
            else:
                context['error'] = "Text Not Extracted"


    return render(request, "text_analysis.html",context)

@login_required(login_url="log_in")
@cache_control(no_cache = True, must_revalidate = True, no_store = True)
def post_analysis(request):
    if request.method == "POST":
        page_id = request.POST['sentence']
        access_token = 'EAAGzYkt6HrEBO28FZAxh3rxPrqF24l6EpiszRELhzFMQ6VKEMhslelkkTiNXvPeYFZAMXEoSSkMbeYsUr00fGmeLJU4rIC7uOClNOTuKKJgk9RHk5hueC2gEnydCJOzmg4AmdeZAsBj1nGJlqE3uukcAaUUFk7KwjPXhtY8dul3oYavZAZBeYciKKQqF6ZCLBAlP567Xs3'
        posts_url = f"https://graph.facebook.com/{page_id}/posts?fields=id,message,full_picture&access_token=" + access_token
        posts_response = requests.get(posts_url)
        posts_data = posts_response.json()
        textss =[]
        result = []
        for post in posts_data["data"]:
                if "message" in post:
                    text = post["message"]
                    textss.append(text)
                    
                    result1= get_sentiment_score(text)
                    result.append(result1)             

                    print("\n")
                if "full_picture" in post:
                    image_url = post["full_picture"]
                    print(image_url)
                    save_image_to_model(image_url)

                     
        combined_data = list(zip(textss, result))
        return render(request, "post_analysis.html",{"combined_data" : combined_data} )

    context = {
        'fname': request.user.first_name,
    
        }
    return render(request, "post_analysis.html",context)
