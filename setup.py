import numpy
from setuptools import setup, find_packages, Extension
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
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

serlib_cparser = Extension('serlib.cparser',
                            sources=['serlib/cparser.cpp'],
                            include_dirs=[numpy.get_include()],
#                            extra_compile_args = ["-O0",
#                                                  "-fsanitize=address"],
#                            extra_link_args = ["-fsanitize=address",
#                                               "-static-libasan"]
                            )
    
setuptools.setup(
    name='pycoq',
    version='0.0.2',
    author='Vasily Pestun, Fidel I. Schaposnik Massolo',
    packages=['pycoq', 'serlib'],
    ext_modules=[serlib_cparser],
    license='MIT License',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.8',
    install_requires=['lark-parser',
                      'pathos',
                      'tqdm',
                      'aiofile',
                      'dataclasses-json'],
    entry_points={'console_scripts': ['pycoq-trace=pycoq.pycoq_trace:main']},
    platforms = ["Linux"],
    classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],
    dependency_links=['git+https://github.com/pestun/strace-parser@c3f0d87#egg=strace-parser',
                      'git+https://github.com/pestun/coq-serapi#v8.11.dev']
    )


