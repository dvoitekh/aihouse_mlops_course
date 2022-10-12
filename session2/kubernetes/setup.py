from setuptools import setup, find_packages

requirements = [l.strip() for l in open('requirements.txt', 'r').readlines() if len(l) > 1 and not l[0:4] == 'http']

setup(
    name='ml-service-demo',
    version='0.0.1',

    description='ML Service Demo',
    long_description='ML Service Demo',

    keywords='ml microservice',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    include_package_data=True,
    install_requires=requirements,

    extras_require={
        'dev': [],
        'test': [],
    },
    package_data={},
    data_files=[],
)
