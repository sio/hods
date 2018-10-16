from setuptools import setup, find_packages

setup(
    name='hods',
    version='0.1.0-git',
    description='Human oriented data storage (library and tools)',
    url='https://github.com/sio/hods',
    author='Vitaly Potyarkin',
    author_email='sio.wtf@gmail.com',
    license='Apache',
    platforms='any',
    entry_points={
        'console_scripts': ['hods=hods.cli:main'],
    },
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    install_requires=[
        'jsonschema',
        'strictyaml',
        'ruamel.yaml',
        'setuptools',
    ],
    python_requires='>=3.3',
    zip_safe=True,
)
