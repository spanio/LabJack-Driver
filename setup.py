from setuptools import setup, find_packages

setup(
    name='LabjackClient',  
    version='0.1.0', 
    packages=find_packages(), 
    install_requires=[
        'labjack-ljm',
    ],
    description='LabJack T7 driver package for Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Brian Benchoff',
    author_email='brian.benchoff@span.io',
    url='https://github.com/spanio/Labjack-Driver', 
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
