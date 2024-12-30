# локальная установка
python3 -m venv venv
source venv/bin/activate
pip install -e .

# тулза
pip install twine

# Упаковка 
rm dist/*
pip install setuptools
python setup.py sdist

# аплоэд
twine upload dist/*


Старая версия заливки
---------------------

# Регистрация и авторизация
python setup.py register

# Загрузка
python setup.py sdist upload
