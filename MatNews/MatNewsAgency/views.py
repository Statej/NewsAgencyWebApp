# Create your views here.
from django.http import HttpResponseNotFound, HttpResponseBadRequest, HttpResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from .models import Author, Article
from datetime import datetime
import json


# This view logs in the user using a POST request, sending in the username and password
@csrf_exempt
def loginUser(request):
    if request.method == 'POST':
        # Check if username and password are present in the POST data
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        if username is None or password is None:
            # If either username or password is missing, return a 400 Bad Request error
            return HttpResponseBadRequest("Username and password are required.", content_type='text/plain')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse("Welcome, {}!".format(username), content_type='text/plain')
        else:
            return HttpResponseNotFound("No user found for that combination of username and password.", content_type='text/plain')
    else:
        # If request method is not POST, return a 400 Bad Request error
        return HttpResponseBadRequest("Only POST requests are allowed.", content_type='text/plain')
    
# This view logs out the user
@csrf_exempt
def logoutUser(request):
    # Check if this is a POST request
    if request.method != 'POST':
        return HttpResponseBadRequest("Only POST requests are allowed.", content_type='text/plain')
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        return HttpResponse("Goodbye, {}!".format(username), content_type='text/plain')
    else:
        return HttpResponseNotFound("No user is currently logged in.", content_type='text/plain')
    
@csrf_exempt
def post_or_get_article(request):
    if request.method == 'POST':
        return post_article(request)
    elif request.method == 'GET':
        return get_articles(request)
    else:
        return HttpResponseBadRequest("Only POST and GET requests are allowed.", content_type='text/plain')

# This view receives a JSON payload with all the required data to post a new article, checks if the user is logged in, and if so, creates the article
@csrf_exempt
def post_article(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                payload = json.loads(request.body)
                headline = payload.get('headline', None)
                category = payload.get('category', None)
                region = payload.get('region', None)
                details = payload.get('details', None)
                
                categoryOptions = ['pol', 'tech', 'art', 'trivia']
                regionOptions = ['uk', 'eu', 'w']

                if headline is None or category is None or region is None or details is None:
                    return HttpResponseServerError("You have missed one or more of the required fields, please check your payload.", content_type='text/plain')
                if category not in categoryOptions or region not in regionOptions:
                    return HttpResponseServerError("Invalid category or region.", content_type='text/plain')
                if len(headline) > 64 or len(details) > 128:
                    return HttpResponseServerError("Headline or details too long.", content_type='text/plain')
                
            except json.JSONDecodeError:
                return HttpResponseServerError("Invalid JSON payload.", content_type='text/plain')
    
            timestamp = datetime.now()

            # Create the article
            try:
                article = Article(headline=headline, category=category, region=region, author=request.user.author, date=timestamp, details=details)
                article.save()
                # Responds with a 201 CREATED message
                return HttpResponse("Article posted successfully.", content_type='text/plain', status=201)
            except Exception as e:
                return HttpResponseServerError("An error occurred while creating the article: {}".format(e), content_type='text/plain')
        else:
            return HttpResponseServerError("You must be logged in to post an article.", content_type='text/plain')
    else:
        return HttpResponseServerError("Only POST requests are allowed.", content_type='text/plain')
    

# This view gets a GET payload application/x-www-formurlencoded with the category, region and date, and returns a JSON payload with the articles that match the criteria published at or after the date
def get_articles(request):
    if request.method == 'GET':
        # Check if all the required fields are present in the GET payload
        # Get the fields from the GET payload, assume '*' if not provided
        category = request.GET.get('story_cat', '*').strip('"')
        region = request.GET.get('story_region', '*').strip('"')
        date = request.GET.get('story_date', '*').strip('"')

        try:
            # Get the articles that match the criteria
            articles = Article.objects.all()

            if category != '*':
                articles = articles.filter(category=category)
            if region != '*':
                articles = articles.filter(region=region)
            if date != '*':
                articles = articles.filter(date__gte=datetime.strptime(date, '%d/%m/%Y').date())
            if not articles:
                return HttpResponseNotFound("No stories were found.", content_type='text/plain')
            # Create a JSON payload with the articles
            response = {
                "stories": []
            }
            for article in articles:
                # Appends the article to the response and includes the unique key, headline, category, region, author, date and details
                response["stories"].append({
                    "key": article.id,
                    "headline": article.headline,
                    "story_cat": article.category,
                    "story_region": article.region,
                    "author": article.author.name,
                    "story_date": article.date.strftime("%d/%m/%Y"),
                    "story_details": article.details
                })
            return HttpResponse(json.dumps(response), content_type='application/json')
        except Exception as e:
            return HttpResponseServerError("An error occurred while fetching the articles: {}".format(e), content_type='text/plain')
    else:
        return HttpResponseBadRequest("Only GET requests are allowed.", content_type='text/plain')

# The client sends a DELETE request to the url /api/stories/key, where key is the unique key of the article to be deleted, and the server deletes the article if the user is authenticated and is the author of the article
@csrf_exempt
def delete_article(request, key):
    if request.method == 'DELETE':
        if request.user.is_authenticated:
            try:
                article = Article.objects.get(id=key)
                if article.author.user == request.user:
                    article.delete()
                    return HttpResponse("Article deleted successfully.", content_type='text/plain')
                else:
                    return HttpResponse("You are not the author of this article and therefore cannot delete it.", content_type='text/plain', status=503)
            except Article.DoesNotExist:
                return HttpResponse("No article with that key was found.", content_type='text/plain', status=503)
            except Exception as e:
                return HttpResponse("An error occurred while deleting the article: {}".format(e), content_type='text/plain', status=503)
        else:
            return HttpResponse("You must be logged in to delete an article.", content_type='text/plain', status=503)
    else:
        return HttpResponse("Only DELETE requests are allowed.", content_type='text/plain', status=503)
