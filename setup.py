import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(name='vedirect_m8',
      version='1.2.0',
      description='Victron VE.Direct decoder for Python',
      long_description=README,
      long_description_content_type="text/markdown",
      url='https://github.com/mano8/vedirect_m8',
      author='Janne Kario, Eli Serra',
      author_email='eli.serra173@gmail.com',
      license='MIT',
      classifiers=[
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
      ],
      packages=['vedirect_m8'],
      include_package_data=True,
      install_requires=[
          'pytest',
          'pyserial',
          've_utils>=2.0.0',
      ],
      python_requires='>3.5.2',
      zip_safe=False
      )
