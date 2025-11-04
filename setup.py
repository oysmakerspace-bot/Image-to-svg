from setuptools import setup, find_packages

setup(
    name='img-to-svg',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'Pillow',
        'pixels2svg',
    ],
    entry_points={
        'console_scripts': [
            'img-to-svg = img_to_svg.main:main',
        ],
    },
)
