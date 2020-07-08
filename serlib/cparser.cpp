#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <numpy/arrayobject.h>
#include <map>
#include <vector>
using namespace std;

#define OPEN_PARENTHESIS -1
#define CLOSE_PARENTHESIS -2
#define GET_TOKEN_ERROR -3

#define HASH_CONST 5371ULL
#define HASH_BASE 33ULL
#define CONSUME_CHAR(cur_hash, character) ( (cur_hash) = (cur_hash)*HASH_BASE + (character) )

#define PARSING_ERROR -1

//EXCEPTIONS

static PyObject *BufferOverflow;
static PyObject *ParsingError;

//HASH_STRING

extern "C"
unsigned long long _hash_string(const char input_buffer[], int buffer_len) {
    unsigned long long cur_hash = HASH_CONST;
    for (int pos=0; pos<buffer_len; pos++) CONSUME_CHAR(cur_hash, input_buffer[pos]);
    return cur_hash;
}

static PyObject *
cparser_hash_string(PyObject *self, PyObject *args)
{
    const char *input_buffer;
    Py_ssize_t buffer_len;
    
    unsigned long long res;
    
	if (!PyArg_ParseTuple(args, "y#", &input_buffer, &buffer_len))
		return NULL;
    res = _hash_string(input_buffer, buffer_len);
    return PyLong_FromUnsignedLongLong(res);
}

// PARSE

int get_word(char input_buffer[], const int buffer_len, int &pos, map<unsigned long long, int> &dict, int add_dict_buffer[], const int add_dict_buffer_size, int &add_dict_size) {
    int start = pos;
    unsigned long long cur_hash = HASH_CONST;

    if (input_buffer[pos] == '"') {
		CONSUME_CHAR(cur_hash, input_buffer[pos++]);
		while (pos < buffer_len && input_buffer[pos] != '"') {
		    if (input_buffer[pos] == '\\') {
				CONSUME_CHAR(cur_hash, input_buffer[pos++]);
				if (pos == buffer_len) {
					PyErr_SetString(ParsingError, "unexpected EOF while parsing");
					return GET_TOKEN_ERROR;
				}
		    }
		    CONSUME_CHAR(cur_hash, input_buffer[pos++]);
		}
		if (pos == buffer_len) {
			PyErr_SetString(ParsingError, "unexpected EOF while parsing");
			return GET_TOKEN_ERROR;
		}
		CONSUME_CHAR(cur_hash, input_buffer[pos++]);
    } else {
		while (pos < buffer_len) {
		    if (input_buffer[pos]  == '"' || input_buffer[pos]  == '(' || input_buffer[pos]  == ')' || input_buffer[pos]  == ' ') break;
	
		    CONSUME_CHAR(cur_hash, input_buffer[pos++]);
		}
    }
    int end = pos;
    
    if (dict.find(cur_hash) == dict.end()) {
    	if (2*add_dict_size+2 > add_dict_buffer_size) {
    		PyErr_SetString(BufferOverflow, "dictionary buffer overflow");
    		return GET_TOKEN_ERROR;
		}
		dict[cur_hash] = (int)dict.size()+1;
		add_dict_buffer[2*add_dict_size] = start;
		add_dict_buffer[2*add_dict_size+1] = end;
		add_dict_size++;
    }
    return dict[cur_hash];
}

int next_token(char input_buffer[], const int buffer_len, int &pos, map<unsigned long long, int> &dict, int add_dict_buffer[], const int add_dict_buffer_size, int &add_dict_size) {
    while (pos<buffer_len && input_buffer[pos] == ' ') pos++;
    if (input_buffer[pos] == '(') { pos++; return OPEN_PARENTHESIS; }
    else if (input_buffer[pos] == ')') { pos++; return CLOSE_PARENTHESIS; }
    else return get_word(input_buffer, buffer_len, pos, dict, add_dict_buffer, add_dict_buffer_size, add_dict_size);
}

bool address_match(vector<int> &open_parenthesis, int address[], const int num_levels) {
    for (int i = 0; i<num_levels && i<(int)open_parenthesis.size(); i++)
        if (open_parenthesis[i] != address[i]) return false;
    return (num_levels <= (int)open_parenthesis.size());
}

extern "C"
int _parse(char input_buffer[], const int buffer_len, int address[], const int num_levels, unsigned long long hash_list[], const int num_hashes, int output_buffer[], const int output_buffer_size, int &output_size, int add_dict_buffer[], const int add_dict_buffer_size, int &add_dict_size) {
    map<unsigned long long, int> dict;
    for (int i=0; i<num_hashes; i++) dict[hash_list[i]] = i+1;
    
    int pos = 0;
    output_size = 0;
	add_dict_size = 0;
    vector<int> open_parenthesis;
    while (pos < buffer_len) {
		int token = next_token(input_buffer, buffer_len, pos, dict, add_dict_buffer, add_dict_buffer_size, add_dict_size);
		if (token == GET_TOKEN_ERROR) return PARSING_ERROR;
		
		if (token == OPEN_PARENTHESIS) open_parenthesis.push_back(0);
		else if (token == CLOSE_PARENTHESIS) {
			if (open_parenthesis.empty()) {
				PyErr_SetString(ParsingError, "unmatched ')'");
				return PARSING_ERROR;
			}
		    int last_element = open_parenthesis.back();
		    open_parenthesis.pop_back();
		    if (address_match(open_parenthesis, address, num_levels)) {
		    	if (output_size == output_buffer_size) {
		    		PyErr_SetString(BufferOverflow, "output buffer overflow");
		    		return PARSING_ERROR;
				}
				output_buffer[output_size++] = -last_element;
			}
		    if (!open_parenthesis.empty()) open_parenthesis.back() += 1;
		} else {
		    if (address_match(open_parenthesis, address, num_levels)) {
		    	if (output_size == output_buffer_size) {
		    		PyErr_SetString(BufferOverflow, "output buffer overflow");
		    		return PARSING_ERROR;
				}
				output_buffer[output_size++] = token;
			}
		    if (!open_parenthesis.empty()) open_parenthesis.back() += 1;
		}
    }
    if (!open_parenthesis.empty()) {
    	PyErr_SetString(ParsingError, "unmatched '('");
		return PARSING_ERROR;
	}
    return 0;
}

static PyObject *
cparser_parse(PyObject *self, PyObject *args)
{
    char *input_buffer;
    Py_ssize_t buffer_len;
    PyArrayObject *npaddress;
    PyArrayObject *nphash_list;
    PyArrayObject *npoutput_buffer;
    PyArrayObject *npadd_dict_buffer;

    int res;
    int* address;
    int address_len;
    unsigned long long * hash_list;
    int hash_list_len;
    int* output_buffer;
    int output_buffer_size;
    int output_size;
    int* add_dict_buffer;
    int add_dict_buffer_size;
    int add_dict_size;

    if (!PyArg_ParseTuple(args, "y#O!O!iO!O!",
						  &input_buffer, &buffer_len,
						  &PyArray_Type, &npaddress,
						  &PyArray_Type, &nphash_list,
						  &hash_list_len, 
						  &PyArray_Type, &npoutput_buffer,
						  &PyArray_Type, &npadd_dict_buffer))
		return NULL;
    address = (int*) PyArray_DATA(npaddress);
    address_len = PyArray_SIZE(npaddress);

    hash_list = (unsigned long long *) PyArray_DATA(nphash_list);
    
    output_buffer = (int*) PyArray_DATA(npoutput_buffer);
    output_buffer_size = PyArray_SIZE(npoutput_buffer);
    
    add_dict_buffer = (int*) PyArray_DATA(npadd_dict_buffer);
    add_dict_buffer_size = PyArray_SIZE(npadd_dict_buffer);

    res = _parse(input_buffer, buffer_len, address, address_len, hash_list, hash_list_len, output_buffer, output_buffer_size, output_size, add_dict_buffer, add_dict_buffer_size, add_dict_size);
    if (res == PARSING_ERROR) return NULL;
    
    return Py_BuildValue("ii", output_size, add_dict_size);
}

//MODULE DEFINITIONS

static PyMethodDef CParserMethods[] = {
    {"hash_string", cparser_hash_string, METH_VARARGS, "Hash a bytestring"},   /* python function name, c function name, _ , doc string" */
    {"parse", cparser_parse, METH_VARARGS, "Parse a bytestring"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef cparsermodule = {
    PyModuleDef_HEAD_INIT,
    "cparser",   /* name of module */
    "cparser is C extension module implementing hash_string() and parse()",  /* doc string */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    CParserMethods
};

PyMODINIT_FUNC
PyInit_cparser(void)
{
    import_array(); 

	PyObject *module;

	module = PyModule_Create(&cparsermodule);
    if (module == NULL) return NULL;

	BufferOverflow = PyErr_NewException("cparser.BufferOverflow", NULL, NULL);
	Py_XINCREF(BufferOverflow);
	if (PyModule_AddObject(module, "BufferOverflow", BufferOverflow) < 0) {
        Py_XDECREF(BufferOverflow);
        Py_CLEAR(BufferOverflow);
        Py_DECREF(module);
        return NULL;
    }
	
	ParsingError = PyErr_NewException("cparser.ParsingError", NULL, NULL);
    Py_XINCREF(ParsingError);
    if (PyModule_AddObject(module, "ParsingError", ParsingError) < 0) {
        Py_XDECREF(ParsingError);
        Py_CLEAR(ParsingError);
        Py_DECREF(module);
        return NULL;
    }

    return module;
}
