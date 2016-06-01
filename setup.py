from setuptools import setup

setup(
    name='tagy',
    version='0.1.4',
    description='Static site generator',
#    long_description = open("README.md").read(),
    url='https://github.com/melnikov-ivan/tagy',
    author='Ivan Melnikov',
    author_email='melnikov.ivan@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'
    ],
    keywords='Jinja2 fully customizable static site generator',

    # packages=find_packages(exclude=['contrib', 'docs', 'tests'])
    py_modules=["tagy"],
    install_requires=[
       'Jinja2==2.7',
        'PyYAML',
        'mistune==0.7.2',
        'Pillow',
    ],
)
