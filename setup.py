from setuptools import setup


setup(name='Kamanian',
      version='2.0.0',
      packages=['dydz',
                'dydz.dcore',
                'dydz.mcore',
                'dydz.abmodel',
                'dydz.ebmodel',
                'dydz.multimodel'],
      install_requires=['pandas', 'numpy', 'scipy', 'matplotlib',
                        'networkx', 'factory', 'PyEpiDAG'],
      )
