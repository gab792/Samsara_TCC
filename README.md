# Samsara TCC

# Como subir o ambiente

1. Criar e ativar o .venv
```bash
python -m venv .venv
cd .venv/Scripts
activate
cd ../..
```

2. Criar e alterar o .env
```bash
copy .env.example .env
```

3. Baixar as bibliotecas pip
```bash
pip install -r requirements.txt
```

4. Aplicar a migrade do banco de dados
```bash
flask db upgrade
```

5. Subir a aplicação
```bash
python main.py
```
> Aplicação estará disponível no localhost:5000 (http://127.0.0.1:5000/)