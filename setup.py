import os
import setuptools
import numpy

from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


CLASSIFIERS = """\
Development Status :: 1 - Planning
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: C
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3 :: Only
Programming Language :: Python :: Implementation :: CPython
Topic :: Scientific/Engineering :: Artificial Intelligence
Operating System :: POSIX :: Linux
"""

serlib_cparser = setuptools.Extension('serlib.cparser',
                            sources=['serlib/cparser.cpp'],
                            include_dirs=[numpy.get_include()],
                            extra_compile_args = ["-std=c++14"],
                            )
    
setuptools.setup(
    name='pycoq',
    version='0.0.1a1dev2',
    author='Vasily Pestun, Fidel I. Schaposnik Massolo',
    author_email='pestun@ihes.fr',
    packages=['pycoq', 'serlib', 'pycoq.test'],
    ext_modules=[serlib_cparser],
    license='MIT License',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/IBM/pycoq',
    python_requires='>=3.8',
    include_package_data=True,
    package_data={'pycoq': ['test/*',
                            'test/autoagent/*',
                            'test/lf/*',
                            'test/coq-bignums/*',
                            'test/query_goals/*',
                            'test/serlib/*',
                            'test/trace/*']},
    install_requires=['lark-parser',
                      'pylint',
                      'pathos',
                      'ipython',
                      'ipykernel',
                      'rope',
                      'pathos',
                      'tqdm',
                      'aiofile',
                      'pytest',
                      'strace-parser',
                      'pytest-benchmark',
                      'dataclasses-json',
                      'numpy'],
        entry_points={'console_scripts': ['pycoq-trace=pycoq.pycoq_trace:main']},
    project_urls={
        'Source': 'https://github.com/pestun/pycoq'
    },
    platforms = ["Linux"],
    classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],
    )
