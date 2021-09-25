#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <numpy/arrayobject.h>
#include <map>
#include <vector>
#include <algorithm>

#define OPEN_PARENTHESIS -1
#define CLOSE_PARENTHESIS -2
#define GET_TOKEN_ERROR -3

#define HASH_CONST 5371ULL
#define HASH_BASE 257ULL
#define CONSUME_CHAR(cur_hash, character) ( (cur_hash) = (cur_hash)*HASH_BASE + (character) )

#define PARSING_ERROR -1

//EXCEPTIONS

static PyObject *BufferOverflow;
static PyObject *ParsingError;
static PyObject *IndexError;

static PyObject* numpy_ndarray1d_int(const std::vector<int>& a) {
    // creates PyObject numpy.ndarray of dtype=np.intc from std::vector<int>
    npy_intp dims[1] = {(npy_intp)a.size()};
    PyObject* res = PyArray_SimpleNew(1, dims, NPY_INT);
    int* res_data = (int*) PyArray_DATA((PyArrayObject*)res);
    std::copy(a.begin(), a.end(), res_data);
    return res;
}

static PyObject* numpy_ndarray1d_intp(const std::vector<npy_intp>& a) {
    // creates PyObject numpy.ndarray of dtype=np.intc from std::vector<int>
    npy_intp dims[1] = {(npy_intp)a.size()};
    PyObject* res = PyArray_SimpleNew(1, dims, NPY_INTP);
    npy_intp* res_data = (npy_intp*) PyArray_DATA((PyArrayObject*)res);
    std::copy(a.begin(), a.end(), res_data);
    return res;
}



static PyObject*
annotate(PyObject *self, PyObject *args) {
    PyArrayObject* np_vector;

    if (!PyArg_ParseTuple(args, "O!",
			  &PyArray_Type, &np_vector)) {
	return NULL;
    }

    int* v = (int*) PyArray_DATA(np_vector);
    int len_v = PyArray_SIZE(np_vector);

    npy_intp dims[1] = {(npy_intp)len_v};
    PyObject* res = PyArray_SimpleNew(1, dims, NPY_INT);
    int* res_data = (int*) PyArray_DATA((PyArrayObject*)res);

    for (int i = 0; i < len_v; ++i) {
	if (v[i] > 0) {
	    res_data[i] = i;
	} else {
	    int repeat = - v[i];
	    int start = i;
	    while (repeat--) {
		start = res_data[start - 1];
	    }
	    res_data[i] = start;
	}
    }
    return res;
}

static PyObject*
children(PyObject *self, PyObject *args) {
    // children(postfix: numpy.ndarray[int], ann: numpy.ndarray[int], node_index: int) -> numpy.ndarray[int]
    // returns the child node indices
    // None if the child is an atom
    PyArrayObject* np_postfix;
    PyArrayObject* np_ann;
    int node_index;
    if (!PyArg_ParseTuple(args, "O!O!i",
			  &PyArray_Type, &np_postfix,
			  &PyArray_Type, &np_ann,
			  &node_index)) {
	return NULL;
    }

    npy_int* postfix = (npy_int*) PyArray_DATA(np_postfix);
    npy_intp postfix_len = PyArray_SIZE(np_postfix);

    npy_int* ann = (npy_int*) PyArray_DATA(np_ann);

    if (!(node_index >= 0 && node_index < postfix_len)) {
	PyErr_SetString(IndexError, "node index is out of bound");
	return NULL;
    }

    int breadth = -postfix[node_index];

    if (breadth < 0) {
	PyErr_SetString(IndexError, "this node is not a list (it must be atom)");
	return NULL;
    }

    std::vector<npy_int> res {};

    while (breadth-- > 0) {
	--node_index;
	res.push_back(node_index);
	node_index = ann[node_index];
    }

    std::reverse(res.begin(), res.end());

    return numpy_ndarray1d_int(res);
}

static PyObject*
subtree(PyObject *self, PyObject *args) {
    PyArrayObject* np_postfix;
    PyArrayObject* np_ann;
    PyArrayObject* np_address;

    if (!PyArg_ParseTuple(args, "O!O!O!",
			  &PyArray_Type, &np_postfix,
			  &PyArray_Type, &np_ann,
			  &PyArray_Type, &np_address)) {
	return NULL;
    }

    int* postfix = (int*) PyArray_DATA(np_postfix);
    int postfix_len = PyArray_SIZE(np_postfix);

    int* ann = (int*) PyArray_DATA(np_ann);


    int* address = (int*) PyArray_DATA(np_address);
    int address_len = PyArray_SIZE(np_address);

    int end_pos = postfix_len;
    for (int i = 0; i < address_len; ++i) {
	--end_pos;
	if (end_pos < 0) {
	    PyErr_SetString(IndexError, "index address is too long");
	    return NULL;
	}
	int breadth = -postfix[end_pos];
	if (address[i] < 0 || address[i] >= breadth) {
	    PyErr_SetString(IndexError, "index address is out of bounds");
	    return NULL;
	}
	int skip = breadth - address[i] - 1;
	for (int j = 0; j < skip; ++j) {
	    end_pos = ann[end_pos - 1];
	}
    }
    int start_pos = ann[end_pos - 1];
    return Py_BuildValue("ii", start_pos, end_pos);
}


static PyObject* cparser_test(PyObject *self, PyObject *args)
// https://codereview.stackexchange.com/questions/92266/sending-a-c-array-to-python-numpy-and-back
// https://stackoverflow.com/questions/18780570/passing-a-c-stdvector-to-numpy-array-in-python    
{
    std::vector<npy_int> a {1,2,3,4,5};
    return numpy_ndarray1d_int(a);
}



//HASH_STRING
static unsigned long long _hash_string(const char input_buffer[], Py_ssize_t buffer_len) {
    unsigned long long cur_hash = HASH_CONST;
    for (Py_ssize_t pos = 0; pos < buffer_len; ++pos) {
	CONSUME_CHAR(cur_hash, input_buffer[pos]);
    }
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


int get_word(char input_buffer[], const Py_ssize_t buffer_len, Py_ssize_t &pos, std::map<unsigned long long, int> &dict, std::vector<npy_intp> &np_add_dict) {
    Py_ssize_t start = pos;
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
    Py_ssize_t end = pos;
    
    if (dict.find(cur_hash) == dict.end()) {
	dict[cur_hash] = (int)dict.size()+1;
	np_add_dict.push_back(start);
	np_add_dict.push_back(end);
    }
    return dict[cur_hash];
}


int next_token(char input_buffer[], const int buffer_len, Py_ssize_t &pos, std::map<unsigned long long, int> &dict, std::vector<npy_intp> &np_add_dict) {
    while (pos<buffer_len && input_buffer[pos] == ' ') pos++;
    if (input_buffer[pos] == '(') { pos++; return OPEN_PARENTHESIS; }
    else if (input_buffer[pos] == ')') { pos++; return CLOSE_PARENTHESIS; }
    else return get_word(input_buffer, buffer_len, pos, dict, np_add_dict);
}

bool address_match(std::vector<int> &open_parenthesis, int address[], const int address_len) {
    for (int i = 0; i<address_len && i<(int)open_parenthesis.size(); i++)
        if (open_parenthesis[i] != address[i]) return false;
    return (address_len <= (int)open_parenthesis.size());
}


extern "C"
int _parse(char input_buffer[], const Py_ssize_t buffer_len, int address[], const int address_len,
	   unsigned long long hash_list[], const int hash_list_len, std::vector<int> &np_output_buffer,
	   std::vector<npy_intp> &np_add_dict,
	   Py_ssize_t &start_pos, Py_ssize_t &end_pos) {
    std::map<unsigned long long, int> dict;
    for (int i=0; i<hash_list_len; i++) dict[hash_list[i]] = i+1;
    
    Py_ssize_t pos = 0;
    std::vector<int> open_parenthesis;
    start_pos = -1;
    while (pos < buffer_len) {
	if (address_match(open_parenthesis, address, address_len) && start_pos == -1) {
	    start_pos = pos;
	}
	int token = next_token(input_buffer, buffer_len, pos, dict, np_add_dict);
	if (token == GET_TOKEN_ERROR) return PARSING_ERROR;
		
	if (token == OPEN_PARENTHESIS) {
	    open_parenthesis.push_back(0);
	}
	else if (token == CLOSE_PARENTHESIS) {
	    if (open_parenthesis.empty()) {
		PyErr_SetString(ParsingError, "unmatched ')'");
		return PARSING_ERROR;
	    }
	    int last_element = open_parenthesis.back();
	    open_parenthesis.pop_back();
	    if (address_match(open_parenthesis, address, address_len)) {
		np_output_buffer.push_back(-last_element);
		end_pos = pos;
	    }
	    if (!open_parenthesis.empty()) open_parenthesis.back() += 1;
	} else {
	    if (address_match(open_parenthesis, address, address_len)) {
		np_output_buffer.push_back(token);
		end_pos = pos;
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

    int res;  // returns error code of type int
    int* address;
    int address_len;
    unsigned long long *hash_list;
    int hash_list_len;


    Py_ssize_t start_pos = -1;
    Py_ssize_t end_pos = -1;

    if (!PyArg_ParseTuple(args, "y#O!O!i",
			  &input_buffer, &buffer_len,
			  &PyArray_Type, &npaddress,
			  &PyArray_Type, &nphash_list,
			  &hash_list_len)) {
	return NULL;
    }
    address = (int*) PyArray_DATA(npaddress);
    address_len = PyArray_SIZE(npaddress);

    hash_list = (unsigned long long *) PyArray_DATA(nphash_list);
    
    std::vector<int> np_output_buffer {};
    std::vector<npy_intp> np_add_dict {};
    
    res = _parse(input_buffer, buffer_len, address, address_len, hash_list, hash_list_len, np_output_buffer, np_add_dict, start_pos, end_pos);
    if (res == PARSING_ERROR) return NULL;
    
    return Py_BuildValue("nnOO", 
			 start_pos, end_pos,
			 numpy_ndarray1d_int(np_output_buffer),
			 numpy_ndarray1d_intp(np_add_dict));

}





//Module DEFINITIONS

static PyMethodDef CParserMethods[] = {
    {"hash_string", cparser_hash_string, METH_VARARGS, "Hash a bytestring"},
    /* python function name, c function name, _ , doc string" */
    {"parse", cparser_parse, METH_VARARGS, "Parse a bytestring"},
    {"annotate", annotate, METH_VARARGS, "annotate postfix representation"},
    {"subtree", subtree, METH_VARARGS, "return subtree slice given postfix representation, annotation, address"},
    {"test", cparser_test, METH_VARARGS, "return numpy array"},
    {"children", children, METH_VARARGS, "return children given postfix, ann, node_index"},
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

    IndexError = PyErr_NewException("cparser.IndexError", NULL, NULL);
    Py_XINCREF(IndexError);
    if (PyModule_AddObject(module, "IndexError", IndexError) < 0) {
        Py_XDECREF(IndexError);
        Py_CLEAR(IndexError);
        Py_DECREF(module);
        return NULL;
    }

    return module;
}
