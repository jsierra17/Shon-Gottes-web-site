@echo off
echo Iniciando la aplicacion web...

IF NOT EXIST venv (
    echo Creando entorno virtual...
    python -m venv venv
    call venv\Scripts\activate
    echo Instalando dependencias...
    pip install -r requirements.txt
) ELSE (
    call venv\Scripts\activate
)

echo Iniciando el servidor...
python app.py
