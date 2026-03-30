#define PY_SSIZE_T_CLEAN
#include <Python.h>

// The actual C function
static PyObject* hello_world(PyObject* self, PyObject* args) {
    return PyUnicode_FromString("Hello, World!");
}

// Optional: hello with a name
static PyObject* hello_name(PyObject* self, PyObject* args) {
    const char* name;
    if (!PyArg_ParseTuple(args, "s", &name))
        return NULL;
    return PyUnicode_FromFormat("Hello, %s!", name);
}

// Method table — lists all functions exposed to Python
static PyMethodDef HelloMethods[] = {
    {"hello_world", hello_world, METH_NOARGS,  "Prints Hello, World!"},
    {"hello_name",  hello_name,  METH_VARARGS, "Prints Hello, <name>!"},
    {NULL, NULL, 0, NULL}  // Sentinel — marks end of the table
};

// Module definition
static struct PyModuleDef hellomodule = {
    PyModuleDef_HEAD_INIT,
    "hellomodule",   // Module name
    NULL,            // Module docstring (optional)
    -1,              // -1 means module keeps state in global variables
    HelloMethods
};

// Module init function — Python calls this on import
PyMODINIT_FUNC PyInit_hellomodule(void) {
    return PyModule_Create(&hellomodule);
}
