@echo off
echo Configurando ambiente de desenvolvimento...
echo .

if not exist .venv (
    echo Criando ambiente virtual...
    python -m venv .venv
) else (
    echo Ambiente virtual ja existe.
)

call .venv\Scripts\activate

echo .
echo Atualizando pip...
python -m pip install --upgrade pip

echo .
echo Instalando dependencias...
python -m pip install -r requirements.txt

if not exist .env (
    echo .
    echo Criando arquivo .env a partir do .env.example...
    copy .env.example .env
) else (
    echo .
    echo Arquivo .env ja existe.
)

echo .
echo Aplicando migrations...
flask db upgrade

echo.
echo Projeto configurado com sucesso.
pause