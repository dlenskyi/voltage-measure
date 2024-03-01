from setuptools import setup, find_packages


setup(
    name='voltage-measure',
    version='0.1.0',
    author='Denys Lenskyi',
    author_email='denis.lenskyi@gmail.com',
    description='Program developed for Raspberry Pi, for the purpose of measuring voltage, '
                'converted by ADS1115, and further processing data',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
