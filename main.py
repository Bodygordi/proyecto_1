{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "private_outputs": true,
      "provenance": []
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "aipfl1bGqlHG"
      },
      "outputs": [],
      "source": [
        "import pandas as pd\n",
        "from sklearn.feature_extraction.text import TfidfVectorizer\n",
        "from sklearn.metrics.pairwise import cosine_similarity\n",
        "from sklearn.metrics.pairwise import linear_kernel\n",
        "import math\n",
        "\n",
        "\n",
        "\n",
        "from fastapi import FastAPI, Response\n",
        "import uvicorn\n",
        "\n",
        "\n",
        "app = FastAPI(title = 'Proyecto indi_1',\n",
        "              description = 'Creación Api',\n",
        "              version = '1.0.1')\n",
        "\n",
        "@app.get(\"/\")\n",
        "async def index():\n",
        "    return ('Construyendo mi Api')\n",
        "\n",
        "@app.get('/about')\n",
        "async def about():\n",
        "    return ('Mi primer proyecto')\n",
        "\n",
        "movies_df = None  # Variable global para almacenar los datos del archivo CSV\n",
        "\n",
        "@app.on_event('startup')\n",
        "async def load_data():\n",
        "    global movies_df\n",
        "\n",
        "    movies_df = pd.read_csv('movies_credits_transform2.csv')\n",
        "\n",
        "@app.get(\"/cantidad_filmaciones_mes\")\n",
        "async def cantidad_filmaciones_mes(Mes: int):\n",
        "    if Mes < 1 or Mes > 12:\n",
        "        return {\"mensaje\": f\"El número de mes '{Mes}' no es válido. Por favor, ingresa un número de mes válido (1-12).\"}\n",
        "\n",
        "    # Convierto la columna de fechas a formato datetime\n",
        "    movies_df['release_date'] = pd.to_datetime(movies_df['release_date'])\n",
        "\n",
        "    # Filtro las películas por el mes consultado\n",
        "    filtro = movies_df['release_date'].dt.month == Mes\n",
        "    peliculas_mes = movies_df[filtro]\n",
        "\n",
        "    # Elimino los registros duplicados basándose en la columna 'id'\n",
        "    peliculas_mes_unique = peliculas_mes.drop_duplicates(subset='id')\n",
        "\n",
        "    # Para obtener la cantidad de películas en el mes consultado\n",
        "    cantidad = len(peliculas_mes_unique)\n",
        "\n",
        "    return {\"mensaje\": f\"{cantidad} cantidad de películas fueron estrenadas en el mes número {Mes}\"}\n",
        "\n",
        "@app.get(\"/cantidad_filmaciones_dia\")\n",
        "async def cantidad_filmaciones_dia(Dia: str):\n",
        "    # Convierto el día en idioma español a minúsculas\n",
        "    dia_lower = Dia.lower()\n",
        "\n",
        "    # Mapeo los nombres de los días en español a los nombres en inglés\n",
        "    dias = {\n",
        "        \"lunes\": \"Monday\",\n",
        "        \"martes\": \"Tuesday\",\n",
        "        \"miércoles\": \"Wednesday\",\n",
        "        \"jueves\": \"Thursday\",\n",
        "        \"viernes\": \"Friday\",\n",
        "        \"sábado\": \"Saturday\",\n",
        "        \"domingo\": \"Sunday\"\n",
        "    }\n",
        "    dia_ingles = dias.get(dia_lower)\n",
        "\n",
        "    if not dia_ingles:\n",
        "        return {\"mensaje\": f\"El día '{Dia}' no es válido. Por favor, ingresa un día válido en español.\"}\n",
        "\n",
        "    # Convierto la columna de fechas a formato datetime\n",
        "    movies_df['release_date'] = pd.to_datetime(movies_df['release_date'])\n",
        "\n",
        "    # Filtro las películas por el día consultado\n",
        "    filtro = movies_df['release_date'].dt.day_name().str.lower() == dia_ingles.lower()\n",
        "    peliculas_dia = movies_df[filtro]\n",
        "\n",
        "    # Obtengo la cantidad de películas en el día consultado\n",
        "    cantidad = len(peliculas_dia)\n",
        "\n",
        "    return {\"mensaje\": f\"{cantidad} cantidad de películas fueron estrenadas en el día {Dia}\"}\n",
        "\n",
        "@app.get(\"/score_titulo/{titulo_de_la_filmacion}\")\n",
        "async def score_titulo(titulo_de_la_filmacion: str):\n",
        "    # Buscamos la película por título en el dataframe\n",
        "    pelicula = movies_df[movies_df['title'] == titulo_de_la_filmacion]\n",
        "\n",
        "    # Verifico si se encontró la película\n",
        "    if pelicula.empty: # El método empty devuelve True si el DataFrame está vacío.\n",
        "        return \"Película no encontrada\"\n",
        "\n",
        "    # Obtengo los valores de título, año de estreno y score\n",
        "    titulo = pelicula['title'].iloc[0] # iloc[0] sirve para acceder al primer registro\n",
        "    año_estreno = str(pelicula['release_year'].iloc[0])\n",
        "    score = str(pelicula['popularity'].iloc[0])\n",
        "\n",
        "    # return f\"La pelicula {titulo} fue estrenada en el año {año_estreno} con un score de {score}.\"\n",
        "    return {'titulo':titulo, 'anio':año_estreno, 'popularidad':score}\n",
        "\n",
        "@app.get(\"/votos_titulo\")\n",
        "async def votos_titulo(titulo_de_la_filmacion: str):\n",
        "    # Filtra la película por el título\n",
        "    filtro = movies_df['title'] == titulo_de_la_filmacion\n",
        "    pelicula = movies_df[filtro]\n",
        "\n",
        "    if pelicula.empty:\n",
        "        return {\"mensaje\": f\"No se encontró ninguna filmación con el título '{titulo_de_la_filmacion}'.\"}\n",
        "\n",
        "    # Obtiene el título de la película\n",
        "    titulo_de_la_filmacion = pelicula['title'].values[0]\n",
        "    # Obtiene la cantidad de valoraciones de la película\n",
        "    cantidad_votos = pelicula['vote_count'].values[0]\n",
        "\n",
        "    if cantidad_votos < 2000:\n",
        "        return {\"mensaje\": f\"La filmación '{titulo_de_la_filmacion}' no cumple con la condición de tener al menos 2000 valoraciones.\"}\n",
        "\n",
        "    # Obtiene el valor promedio de las votaciones de la película\n",
        "    valor_promedio = pelicula['vote_average'].values[0]\n",
        "\n",
        "    # Obtiene el año de estreno de la película\n",
        "    año_estreno = pelicula['release_year'].values[0]\n",
        "\n",
        "    return {\"mensaje\": f\"La película '{titulo_de_la_filmacion}' fue estrenada en el año {año_estreno}. Cuenta con un total de {cantidad_votos} valoraciones, con un promedio de {valor_promedio}\"}\n",
        "\n",
        "@app.get(\"/get_actor\")\n",
        "async def get_actor(nombre_actor: str):\n",
        "    for _, row in movies_df.iterrows():   # iteramos sobre las filas del dataframe\n",
        "        actores = row[\"actores\"]\n",
        "        if nombre_actor.lower() in actores.lower():\n",
        "            peliculas = len(actores.split(\",\"))   # la cantidad de peliculas en la que ha participado un actor.\n",
        "            retorno_total = row[\"return\"]\n",
        "            if peliculas > 0:\n",
        "                retorno_promedio = retorno_total / peliculas\n",
        "            else:\n",
        "                retorno_promedio = 0\n",
        "\n",
        "            return {\n",
        "                \"mensaje\": f\"El actor {nombre_actor} ha participado en {peliculas} películas, \"\n",
        "                           f\"con un retorno total de {retorno_total} y un promedio de {retorno_promedio} por película.\"\n",
        "            }\n",
        "    return {\"mensaje\": f\"No se encontró ningún actor con el nombre {nombre_actor}.\"}\n",
        "\n",
        "\n",
        "@app.get(\"/get_director\")\n",
        "async def get_director(nombre_director: str):\n",
        "    peliculas_director = []\n",
        "\n",
        "    for _, row in movies_df.iterrows():\n",
        "        directores = row[\"Directores\"]\n",
        "        if isinstance(directores, str) and nombre_director.lower() in directores.lower():\n",
        "            titulo = row[\"title\"]\n",
        "            fecha_lanzamiento = row[\"release_date\"]\n",
        "            retorno = row[\"return\"]\n",
        "            if isinstance(retorno, float) and retorno == 0.0:\n",
        "                retorno = \"inf\"\n",
        "            pelicula = {\n",
        "                \"titulo\": titulo,\n",
        "                \"fecha_lanzamiento\": fecha_lanzamiento,\n",
        "                \"retorno\": retorno\n",
        "            }\n",
        "            peliculas_director.append(pelicula)\n",
        "\n",
        "    if len(peliculas_director) > 0:\n",
        "        mensaje = f\"El director {nombre_director} ha dirigido las siguientes películas:\"\n",
        "        return {\"mensaje\": mensaje, \"peliculas\": peliculas_director}\n",
        "\n",
        "    return {\"mensaje\": f\"No se encontró ninguna película dirigida por {nombre_director}.\"}\n",
        "\n",
        "\n",
        "@app.on_event('startup')\n",
        "async def load_data():\n",
        "    global movies_ML\n",
        "\n",
        "\n",
        "    movies_ML = pd.read_csv('movies_ML_parcial.csv')\n",
        "\n",
        "# Defino la nueva función de recomendación con el nuevo dataset\n",
        "@app.get('/recomendacion_nuevo_dataset/{title}')\n",
        "async def get_recomendation_nuevo_dataset(title: str):\n",
        "    # Creao una matriz TF-IDF para el texto del título y overview de las películas\n",
        "    stopwords_custom = [\"where\",\"on\",\"the\", \"at\", \"in\", \"of\",\"and\"]  # Agrega aquí stopwords personalizados\n",
        "    tfidf = TfidfVectorizer(stop_words=stopwords_custom)\n",
        "    tfidf_matrix = tfidf.fit_transform(movies_ML['title']+' '+ movies_ML['overview'])\n",
        "    # Calculo la similitud del coseno entre los títulos de las películas\n",
        "    cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)\n",
        "    # Verifico si el título está en el DataFrame\n",
        "    if title not in movies_ML['title'].values:\n",
        "        return f\"No se encontró ninguna película con el título '{title}'.\"\n",
        "    # Encuentro el índice de la película con el título dado\n",
        "    indices = pd.Series(movies_ML.index, index=movies_ML['title']).drop_duplicates()\n",
        "    idx = indices[title]\n",
        "\n",
        "    # Calculo las puntuaciones de similitud de todas las películas con la película dada\n",
        "    sim_scores = list(enumerate(cosine_similarities[idx]))\n",
        "\n",
        "    # Ordeno las películas por puntaje de similitud en orden descendente\n",
        "    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)\n",
        "    # Obtengo los índices de las películas más similares (excluyendo la película dada)\n",
        "    sim_scores = sim_scores[1:6]  # Obtener las 5 películas más similares\n",
        "    movie_indices = [x[0] for x in sim_scores]\n",
        "\n",
        "   # Devuelvo los títulos de las películas más similares\n",
        "    respuesta_recomendacion = movies_ML['title'].iloc[movie_indices].tolist()\n",
        "    return respuesta_recomendacion\n",
        ""
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "pip install uvicorn"
      ],
      "metadata": {
        "id": "tewrBPHlq2aS"
      },
      "execution_count": null,
      "outputs": []
    }
  ]
}