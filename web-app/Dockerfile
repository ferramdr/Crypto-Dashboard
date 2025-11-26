# Dockerfile para la aplicación web Python
FROM python:3.9-slim

# Etiquetas de metadata
LABEL maintainer="Proyecto Sistemas Distribuidos"
LABEL description="Aplicación web Python para proyecto universitario"

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema (si son necesarias)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de la aplicación (cuando los tengas)
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . .

# Instalar Flask para un servidor web básico por ahora
RUN pip install --no-cache-dir flask pymysql

# Crear un archivo Python básico para mantener el contenedor vivo
RUN echo 'from flask import Flask\n\
    app = Flask(__name__)\n\
    \n\
    @app.route("/")\n\
    def hello():\n\
    return "Web App - Sistemas Distribuidos - Running!"\n\
    \n\
    @app.route("/health")\n\
    def health():\n\
    return {"status": "healthy", "service": "web-app"}\n\
    \n\
    if __name__ == "__main__":\n\
    app.run(host="0.0.0.0", port=8000, debug=True)' > app.py

# Exponer el puerto 8000
EXPOSE 8000

# Comando por defecto: ejecutar la aplicación Flask
CMD ["python", "app.py"]
