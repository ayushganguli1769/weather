from django.shortcuts import render, redirect
import requests
from .models import City
from django.contrib.staticfiles.templatetags.staticfiles import static # way to acess static url
from django.db.models.functions import Lower # converts all fields to lower case for particular model. Doesn't work for individual string
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
@login_required
def weather(request):
    error_message = None #should have been message
    weather_data = []
    weather_url = 'http://api.openweathermap.org/data/2.5/weather?q={city_name}&APPID=76d8701a2522caafc54a59596213c4b2'
    photo_url = 'https://pixabay.com/api/?key=14707317-11f06ab29947093d230acfa68&q={city_name}&image_type=photo&pretty=true'
    if 'add' in request.POST:
        name = request.POST['city_name']
        weather_url_final = weather_url.format(city_name = name)
        responsew = requests.get(weather_url_final)
        dataw = responsew.json()
        weather_status_code = dataw['cod']
        is_exist = City.objects.annotate(my_name = Lower('name')).filter(my_name = name.lower(), user= request.user).exists()#code to check existance of city
        if is_exist == True:
            error_message = "You have already selected the city " + name.lower() + " . Weather data for the city exists in the page."
        elif weather_status_code == 200:
            city = City(name = name, user = request.user)
            city.save()
            error_message = name + " sucessfully added."
        else:
            error_message = "No data for " + name + " exists"

    all_cities = City.objects.filter(user = request.user)
    for city in all_cities:
        name = city.name
        weather_url_final = weather_url.format(city_name = name)
        photo_url_final = photo_url.format(city_name = name)
        responsew = requests.get(weather_url_final)
        responsep = requests.get(photo_url_final)
        dataw = responsew.json()
        datap = responsep.json()
        weather_status_code = dataw['cod']
        totalHits = datap['totalHits']
        if totalHits > 0:
            city_image = datap['hits'][0]['largeImageURL']
        else:
            city_image = static('city.jpg')
        if weather_status_code == 200:
            city_weather ={
            'found': True,
            'city_id': city.id,
            'city': city.name,
            'description':dataw['weather'][0]['description'],
            'temperature': dataw['main']['temp'],
            'pressure': dataw['main']['pressure'],
            'humdity': dataw['main']['humidity'],
            'icon_image': dataw['weather'][0]['icon'],
            'city_image':city_image
            }
        else:
            city_weather = {
                'found': False,
                'city': city.name,
            }
        weather_data.append(city_weather)
    return render(request,'main.html',{'weather_data':weather_data, 'error_message': error_message} )
"""
def addWeather(request):
    if request.method == "POST" and request.POST in 'add':
        name = request.POST['city_name']
        city = City(name = name)
        city.save()
    return render(request,'main.html')

"""
def register(request):
    if 'register' in request.POST:
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            if User.objects.filter(username = username).exists():
                return render(request,'register.html',{'error_message':"Username already taken"})
            elif User.objects.filter(email = email).exists():
                return render(request,'register.html',{'error_message':"Email already taken"})
            else:
                user= User.objects.create_user(username = username, password = password1, email = email, first_name= first_name, last_name = last_name)
                user.save()
                return redirect('/weather/login/')
        else:
            return render(request,'register.html',{'error_message':"Password does not match"})
    return render(request,'register.html')
def login(request):
    if 'login' in request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username = username, password = password)
        if user != None:
            auth.login(request,user)
            return redirect('/weather/')
        else:
            return render(request, 'login.html', {'error_message': "Invalid Credentials"})
    return render(request, 'login.html')
