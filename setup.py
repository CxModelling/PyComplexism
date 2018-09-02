from setuptools import setup, find_packages


setup(name='PyComplexism',
      version='3.2.4',
      packages= find_packages(),
      #['complexism',
      #          'complexism.misc',
      #          'complexism.element',
      #          'complexism.dcore',
      #          'complexism.mcore',
      #          'complexism.agentbased',
      #          'complexism.agentbased.statespace',
      #          'complexism.agentbased.diffeq',
      #          'complexism.equationbased',
      #          'complexism.equationbased.statespace',
      #          'complexism.multimodel'],
      install_requires=['pandas', 'numpy', 'scipy', 'matplotlib',
                        'networkx', 'PyEpiDAG'],
      )
