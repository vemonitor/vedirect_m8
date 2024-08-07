"""Setup Package"""
import pathlib
from setuptools import setup
from vedirect_m8.version import VERSION
# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(name='vedirect_m8',
      version=VERSION,
      packages=['vedirect_m8'],
      package_dir={
            'vedirect_m8': 'vedirect_m8'
      },
      package_data={
            'vedirect_m8': ['sim_data/*.dump']
      },
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
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
      ],
      include_package_data=True,
      install_requires=[
          'pyserial>=3.5',
          've_utils>=2.5.3',
      ],
      extras_require={
              "TEST": [
                    "pytest>=7.4.1",
                    "coverage>=7.3.1"
              ],
              "MQTT": [
                    "paho-mqtt>=1.6.1"
              ]
      },
      python_requires='>3.5.2',
      zip_safe=False
      )
