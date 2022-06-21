import os
from setuptools import setup

base_path = os.path.dirname(__file__)
with open(os.path.join(base_path, "README.md"), encoding='utf-8') as readme_file:
    readme = readme_file.read()

setup(name='crypto_reflex',
      version='1.0.0',
      packages=['crypto_reflex'],
      entry_points={
          'console_scripts': [
              'crypto_reflex = crypto_reflex.main:main'
          ]
      },
      license='MIT',
      description = 'A tool to automatically balance cryptocurrency portfolios',
      long_description=readme,
      long_description_content_type='text/markdown',
      author = 'Draczer01',
      author_email = 'draczer01@gmail.com',
      url = 'https://github.com/draczer01/Crypto_Reflex',
      download_url = 'https://github.com/draczer01/Crypto_Reflex/archive/1.0.0.tar.gz',
      keywords = ['cryptocurrency', 'portfolio', 'xrp', 'ethereum', 'bitcoin', 'btc', 'eth'],
      install_requires=[
          'ccxt',
      ],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Financial and Insurance Industry',
          'Topic :: Office/Business :: Financial :: Investment',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.9',
      ],
      )
