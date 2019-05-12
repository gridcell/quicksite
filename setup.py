from setuptools import setup

install_requires = \
['boto3>=1.9,<2.0',
 'click>=7.0,<8.0',
 'python-cloudflare>=1.0,<2.0',
 'python-magic>=0.4.15,<0.5.0']

setup(
    name='quicksite',
    version='0.1',
    py_modules=['quicksite'],
    install_requires=install_requires,
    entry_points='''
        [console_scripts]
        quicksite=quicksite:cli
    ''',
)