
import ast
import os
from setuptools import setup, find_packages

PACKAGE_NAME = 'whalesong'

path = os.path.join(os.path.dirname(__file__), PACKAGE_NAME, '__init__.py')

with open(path, 'r') as file:
    t = compile(file.read(), path, 'exec', ast.PyCF_ONLY_AST)
    for node in (n for n in t.body if isinstance(n, ast.Assign)):
        if len(node.targets) != 1:
            continue

        name = node.targets[0]
        if not isinstance(name, ast.Name) or \
                name.id not in ('__version__', '__version_info__', 'VERSION'):
            continue

        v = node.value
        if isinstance(v, ast.Str):
            version = v.s
            break
        if isinstance(v, ast.Tuple):
            r = []
            for e in v.elts:
                if isinstance(e, ast.Str):
                    r.append(e.s)
                elif isinstance(e, ast.Num):
                    r.append(str(e.n))
            version = '.'.join(r)
            break

# Get the long description from the README file
with open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='whalesong',

    version=version,

    description='Whalesong is a python library to manage WebApps remotely. Currently WhatsappWeb is implemented',
    long_description=long_description,

    url='https://github.com/alfred82santa/whalesong',

    author='Alfred Santacatalina',
    author_email='alfred82santa@gmail.com',
    include_package_data=True,

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Communications :: Chat',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='WebApp Selenium Web Whatsapp Chat Bot Chatbot',
    packages=find_packages(),
    package_data={PACKAGE_NAME: ['js/whalesong.js',
                                 'firefox_profile_template/*.js',
                                 'firefox_profile_template/*.json']},
    install_requires=[
        'dirty-models>=0.11',
        'python-axolotl',
        'cryptography',
        'aiohttp>=3.0',
        'vobject'
    ],
    extras_require={
        'firefox':  ['selenium>=3.4.3'],
        'chromium': ['pyppeteer',
                     'websockets<7.0'],
    }
)
