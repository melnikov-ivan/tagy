# локальная установка
pip install -e .

# Упаковка 
python setup.py sdist

# Регистрация и авторизация
python setup.py register

# Загрузка
python setup.py sdist upload
