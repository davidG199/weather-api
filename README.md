# weaher api

Api desarrollada con fastApi, se utiliza la api de [OpenWeatherMap](https://openweathermap.org/api) para traer los datos meteorologicos de cada cuidad
se utiliza redis para guardar los datos de las cuidades en la caché, ademas de se implementa una limitacion de peticiones a la api con [slowapi](https://pypi.org/project/slowapi/)

## uso

1. clona este repositorio
2. Crea un entorno virtual
```
py -m venv venv
```
activalo.
```
venv/Scripts/activate
```
3. instala las dependencias
```
pip install -r  requirements.txt
```
4. inicia fastapi
```
uvicorn main:app 
```

[link del reto](https://roadmap.sh/projects/weather-api-wrapper-service)
