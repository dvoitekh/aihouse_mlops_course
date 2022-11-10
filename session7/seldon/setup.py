from setuptools import setup, find_packages

requirements = [l.strip() for l in open('requirements.txt', 'r').readlines() if len(l) > 1]

setup(
    name='seldon_services',
    version='1.0.0',

    description='Seldon Services',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    include_package_data=True,

    install_requires=requirements,

    extras_require={
        'dev': [],
        'test': ['pytest', 'requests', 'jsonschema', 'flake8==3.8.3', 'importlib-metadata==4.13.0'],
    },
    package_data={},
    data_files=[],
    entry_points={}
)
