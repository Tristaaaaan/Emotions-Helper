
import requests
import html

# Set your GPT-3 API key here
openai_api_key = "sk-FNOJtqywZE1fLreUFlwnT3BlbkFJhQRtnlbIEuJEkM2uAW"
openai_api_url = 'https://api.openai.com/v1/chat/completions'

# Set your OpenWeatherMap API key here
weather_api_key = "998ca18b83bdd1414d79ce4f77c30de1"
weather_api_url = "http://api.openweathermap.org/data/2.5/weather"

# Jokes
# Open source
jokes_api_url = "https://v2.jokeapi.dev/joke/Any"
# trivia
# Open source
trivia_api_url = "https://opentdb.com/api.php"

# News
# Developer API is free. I am using the free version
news_api_url = "https://newsapi.org/v2/top-headlines"
news_api_key = "ffd29ba343054dd9872860c04aa76563"

######################### All Integrations Class #########################
##########################################################################

# This class handles all the 3rd party integrations. It uses requests to post the request and parse the response


class AllIntegrations:

    # Integrate with ChatGPT OpenAI APIs.
    def generate_openai_text(self, prompt, max_tokens=60):
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {openai_api_key}'}
        data = {"messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7, 'model': 'gpt-3.5-turbo', }
        response = requests.post(openai_api_url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            choices = result.get("choices", [])
            if choices:
                first_choice = choices[0]
                message = first_choice.get("message", {})
                content = message.get("content", "")
                print("Content:", content)
            else:
                print("No choices in the response.")
            return content + "<br>"
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(response.text)
            return None

    def get_weather_info(self, location):
        params = {'q': location, 'appid': weather_api_key, 'units': 'imperial'}
        response = requests.get(weather_api_url, params=params)
        data = response.json()
        print(f"weather data: {data}")
        if response.status_code == 200:
            weather_description = data['weather'][0]['description']
            temperature = data['main']['temp']
            return f"The weather in {location} is {weather_description}. The current temperature is {temperature}°F."
        return ""

    def get_trivia(self, category="9", difficulty="medium", question_type="multiple"):
        params = {"amount": 1, "category": category,
                  "difficulty": difficulty, "type": question_type, }
        response = requests.get(trivia_api_url, params=params)
        rval = ''
        if response.status_code == 200:
            trivia_data = response.json()
            question = trivia_data.get("results", [])[0]
            decoded_question = html.unescape(question["question"])
            rval += f"Question: {decoded_question} <br>"
            rval += "  \n\n"
            rval += "The options are: <br>\n"
            rval += f"A - {html.unescape(question['correct_answer'])} <br>"
            rval += "  \n"
            rval += f"B - {html.unescape(
                question['incorrect_answers'][0])} <br>"
            rval += "  \n"
            rval += f"C - {html.unescape(
                question['incorrect_answers'][1])} <br>"
            rval += "  \n"
            rval += f"D - {html.unescape(
                question['incorrect_answers'][2])} <br> <br>"
            rval += "  \n"
            rval += "     \n"
            rval += f"The Correct Answer is: {
                html.unescape(question['correct_answer'])} <br>"
        else:
            print(f"Failed to fetch trivia question. Status code: {
                  response.status_code}")
        return rval

    def get_joke(self):
        params = {"format": "json", "type": "twopart", "lang": "en",
                  "category": "programming", "safe-mode": ""}
        response = requests.get(jokes_api_url, params=params, headers={
                                "Accept": "application/json"})
        if response.status_code == 200:
            joke_data = response.json()
            rval = ''
            if joke_data["type"] == "twopart":
                setup, delivery = joke_data["setup"], joke_data["delivery"]
                rval += f"{setup}<br>\n\n{delivery}\n<br>"
            else:
                rval += f"{joke_data['joke']}\n\n"
            rval += "Hope that made you laugh."
        else:
            print(f"Failed to fetch joke. Status code: {response.status_code}")
        return rval

    def get_news(self, country="us", category="general", page_size=2):
        params = {"country": country, "category": category,
                  "pageSize": page_size, "apiKey": news_api_key, }
        rval = ''
        response = requests.get(news_api_url, params=params)
        if response.status_code == 200:
            news_data = response.json()
            articles = news_data.get("articles", [])
            rval += "The News is <br> \n"
            for i, article in enumerate(articles, start=1):
                rval += f"{article['title']}<br>\n\n"
        else:
            print(f"Failed to fetch news. Status code: {response.status_code}")
        return rval
