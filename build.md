# локальная установка
source venv/bin/activate
pip install -e .

#тулза
pip install twine

# Упаковка 
python setup.py sdist

# аплоэд
twine upload dist/*


Старая версия заливки
---------------------

# Регистрация и авторизация
python setup.py register

# Загрузка
python setup.py sdist upload
