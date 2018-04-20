from setuptools import setup


setup(name='PyComplexism',
      version='2.0.0',
      packages=['complexism',
                'complexism.misc',
                'complexism.dcore',
                'complexism.mcore',
                'complexism.abmodel',
                'complexism.ebmodel',
                'complexism.multimodel'],
      install_requires=['pandas', 'numpy', 'scipy', 'matplotlib',
                        'networkx', 'PyEpiDAG'],
      )
