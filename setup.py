from setuptools import setup, find_packages


setup(name='Kamanian',
      version='1.3',
      packages=find_packages(),
      install_requires=['pandas', 'numpy', 'scipy', 'matplotlib', 'networkx'],
      dependency_links=['git+git://github.com/TimeWz667/PyFire.git',]
      )
