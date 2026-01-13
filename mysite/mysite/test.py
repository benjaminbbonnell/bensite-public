import os

print(os.getenv('WEATHER_COM_API_KEY'))
print(os.getenv('SECRET_KEY'))
project_home = '/home/benjaminbbonnell/mysite'
print(os.path.join(project_home, '.env'))
