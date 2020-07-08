CONTEXT_EXT='._pycoq_context'
EXECUTABLE='coqc'
REGEX=r'.*\.v$'
DESCRIPTION=f'''Execute command  <...> from WORKDIR.
  While executing <...>, 
  monitor system calls of EXECUTABLE
  and record the arguments and environment of each call 
  if strictly single argument of a call 
  matches python regex string \'{REGEX}\'. 
  Writes the context to file named argument + {CONTEXT_EXT}
  as a dataclass_json CoqContext object. EXECUTABLE must resolve 
  by shell which. Default value of executable is {EXECUTABLE}.
  Example of usage: pycoq-trace --workdir tests/data/CompCert make'''
