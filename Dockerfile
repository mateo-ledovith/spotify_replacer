# Usa Python 3.9 en Alpine Linux
FROM python:3.9-alpine3.15

# Define el directorio de trabajo
WORKDIR /app

# Copia requirements.txt antes (para aprovechar la cache de Docker)
COPY requirements.txt ./

# Instala dependencias del sistema necesarias para compilaciones y ffmpeg
RUN apk add --no-cache gcc musl-dev libffi-dev ffmpeg

# Instala pip, setuptools y wheel antes de las dependencias
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

# Expone el puerto 5000 para Flask
EXPOSE 5000

# Comando por defecto para ejecutar la app
CMD ["python", "run.py"]
