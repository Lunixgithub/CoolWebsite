from setuptools import setup

setup(
    name='coolwebsite',
    version='0.1.0',
    py_modules=['app'],
    include_package_data=True,
    install_requires=[
        'Flask',
        # add more dependencies here if needed
    ],
)
