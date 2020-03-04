from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(name="SpotPRIS2",
      version='0.3.1',
      author="Adrian Freund",
      author_email="adrian@freund.io",
      url="https://github.com/freundTech/SpotPRIS2",
      description="MPRIS2 interface for Spotify Connect",
      long_description=long_description,
      packages=['spotpris2'],
      package_dir={'spotpris2': "spotpris2"},
      package_data={'spotpris2': ['mpris/*.xml', 'html/*.html']},
      install_requires=[
          "PyGObject",
          "pydbus",
          "spotipy>=2.8",
          "appdirs",
      ],
      entry_points={
          'console_scripts': ["spotpris2=spotpris2.__main__:main"]
      },
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Environment :: No Input/Output (Daemon)",
          "Intended Audience :: End Users/Desktop",
          "License :: OSI Approved :: MIT License",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python :: 3 :: Only",
          "Topic :: Multimedia :: Sound/Audio",
      ],
      python_requires='>=3.6',
      )
