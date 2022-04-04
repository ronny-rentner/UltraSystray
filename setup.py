from setuptools import setup

import sys, pathlib

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

version = '0.0.2'

def glob(*patterns):
    package_path = this_directory / 'UltraSystray'
    icon_path = this_directory / 'icons'
    result = []
    for pattern in patterns:
        result.extend([str(path.relative_to(package_path)) for path in package_path.glob(pattern)])
    return result

setup(
    name='UltraSystray',
    version=version,
    description='Ultra simple cross-platform Python systray icon',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ronny Rentner',
    author_email='ultrasystray.code@ronny-rentner.de',
    url='https://github.com/ronny-rentner/UltraSystray',
    packages=['UltraSystray'],
    #package_dir={'UltraSystray': 'src'},
    zip_safe=False,
    python_requires=">=3.9",
    extras_require={
        ':sys_platform == "win32"': [],
        ':sys_platform == "linux"': ['pygobject'],
        ':sys_platform == "darwin"': [],
    },
    #include_package_data=True,
    package_data={'UltraSystray': glob('../icons/**/*.svg', '../icons/**/*.ico', '../icons/**/*.png')},
)
