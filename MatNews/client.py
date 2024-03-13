import datetime
import json
import requests
import random
session = requests.Session()
currentUrl = "http://127.0.0.1:8000"
directoryUrl = "https://newssites.pythonanywhere.com/api/directory/"

def ax():
    url = "http://127.0.0.1:8000"
    response = session.post(url + "/api/login", data={'username': "statej", 'password': "ahojahoj"})
    print(response.text)

def getNewsAndPrint(category, region, date, desiredUrl, newsName):
    article_categories = {'pol': 'Politics', 'tech': 'Technology News', 'art': 'Art News', 'trivia': 'Trivia News'}
    article_regions = {'uk': 'UK News', 'eu': 'European News', 'w': 'World News'}

    print("Fetching news from " + newsName +"\n")
    try:
        # Make a GET request to the get_articles endpoint sending the payload with the category, region and date in the application/x-www-formurlencoded format
        response = session.get(desiredUrl + "/api/stories", params={'story_cat': category, 'story_region': region, 'story_date': date})
        if response.status_code != 200:
            print("An error occurred while fetching the news: {}".format(response.text))
            return

        # For each object in the JSON response, printax the key, headline, category, region, author, date and details
        for article in response.json()['stories']:
            print("Key: " + str(article['key']))
            print("Headline: " + article['headline'])
            print("Category: " + article_categories[article['story_cat']])
            print("Region: " + article_regions[article['story_region']])
            print("Author: " + article['author'])
            print("Date: " + article['story_date'])
            print("Details: " + article['story_details'])
            print()
    except json.JSONDecodeError:
        print("Invalid JSON payload. This site seems to not be configured correctly")
    except requests.exceptions.Timeout:
        print("Connection timeout, the site might be down or not responding")
    except Exception as e:
        print("An error occurred while fetching the news: {}".format(e))

def login(url):
    try:
        currentUrl = url
        # Ask the user for the username and password
        username = input('Username: ')
        password = input('Password: ')
        # Make a POST request to the login endpoint sending the payload with the username and password in the application/x-www-formurlencoded format 
        response = session.post(url + "/api/login", data={'username': username, 'password': password})
        print(response.text)
    except Exception as e:
        print("An error occurred while logging in: {}".format(e))

def logout():
    # Make a POST request to the logout endpoint
    response = session.post(currentUrl + "/api/logout")
    print(response.text)

def post():
    # Ask the user for the article details
    headline = input('Headline: ')
    category = input('Category: ')
    region = input('Region: ')
    details = input('Details: ')
    # Make a POST request to the post_article endpoint sending the payload with the article details as JSON
    response = session.post(currentUrl + "/api/stories", json={'headline': headline, 'category': category, 'region': region, 'details': details})
    print(response.text)

def news(id, category = "*", region = "*", date = "*"):
    if id == "NOT_PROVIDED":
        print("Fetching news from 20 agencies")
        response = session.get(directoryUrl, timeout=25)
        # Seect 20 random agencies
        random_agencies = random.sample(response.json(), 20)

        # Print the selected objects
        for agency in random_agencies:
            print(agency)
            getNewsAndPrint(category, region, date, agency['url'], agency['agency_name'])
        
    else:
        # TO-DO Delete
        desiredUrl = "http://127.0.0.1:8000"
        newsName = "MatNewsAgency"
        response = session.get(directoryUrl, timeout=25)
        print(response.json())
        for site in response.json():
            if site['agency_code'] == id or site['agency_code'] == id.strip('"'):
                desiredUrl = site['url']
                newsName = site['agency_name']
                break
        if desiredUrl == "":
            print("Invalid id provided, no agency for that code found")
            return
        getNewsAndPrint(category, region, date, desiredUrl, newsName)
        




def list():
    response = session.get(directoryUrl)
    print(response.json())
    for site in response.json():
        print("News Agency: " + site['agency_name'])
        print("URL: " + site['url'])
        print("Agency code: " + site['agency_code'])
        print()

def delete(key):
    if key == "":
        print("No key provided")
        return
    elif key.isdigit() == False:
        print("Invalid key provided")
        return
    # make a DELETE request to the delete_article endpoint sending the key as part of the url
    response = session.delete(currentUrl + "/api/stories/" + key)
    print(response.text)

def exit_program():
    exit()

def process_command(command):
    # Split the command into parts
    parts = command.split(' ')

    # Get the command and arguments
    cmd = parts[0]
    args = parts[1:]

    # Process the command
    
    if cmd == 'login':
        if len(args) == 1:
            login(args[0])
        else:
            print('Invalid command. Usage: login <url>')
    elif cmd == 'logout':
        logout()
    elif cmd == 'post':
        post()
    elif cmd == 'news':
        if len(args) <=4 :
            parsedArgs = {'id': "NOT_PROVIDED", 'category': "*", 'region': "*", 'date': "*"}

            # Create the parser
            for arg in args:
                if arg.startswith("-id="):
                    parsedArgs['id'] = arg.split("=")[1]
                elif arg.startswith("-cat="):
                    parsedArgs['category'] = arg.split("=")[1]
                elif arg.startswith("-reg="):
                    parsedArgs['region'] = arg.split("=")[1]
                elif arg.startswith("-date="):
                    parsedArgs['date'] = arg.split("=")[1].strip('"')

            # check that the date is in the correct format
            if parsedArgs['date'] != "" and parsedArgs['date'] != "*":
                try:
                    print(datetime.datetime.strptime(parsedArgs['date'], '%d/%m/%Y').strftime("%d/%m/%Y"))
                except ValueError:
                    print("Incorrect data format, should be dd/mm/yyyy")
                    return
            # Call the function with the parsed arguments
            news(id=parsedArgs['id'], category=parsedArgs['category'], region=parsedArgs['region'], date=parsedArgs['date'])
        else:
            print('Invalid command. Usage: news [-id=] [-cat=] [-reg=] [-date=]')
    elif cmd == 'list':
        list()
    elif cmd == 'delete':
        if len(args) == 1:
            delete(args[0])
        else:
            print('Invalid command. Usage: delete <key>')
    elif cmd == 'exit':
        exit_program()
    elif cmd == 'ax':
        ax()
    else:
        print('Invalid command.')

def main():
    while True:
        # Read the command from the user
        command = input('> ')

        # Process the command
        process_command(command)

if __name__ == '__main__':
    main()
