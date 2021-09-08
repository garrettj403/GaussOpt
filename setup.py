from setuptools import setup

setup(
    name='GaussOpt',
    version='1.1.3',
    author='John Garrett',
    author_email='garrettj403@gmail.com',
    description='Gaussian beam analysis',
    license='MIT',
    keywords='gaussian optics millimeter terahertz thz',
    url='https://github.com/garrettj403/GaussOpt/',
    packages=['gaussopt',],
    install_requires=[
        'matplotlib',
        'numpy',
        'scipy'
    ],
    long_description=open('README.md').read(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)
