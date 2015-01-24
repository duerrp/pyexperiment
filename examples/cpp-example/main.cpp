#include <Python.h>
#include <iostream>

/* Singleton that interfaces to pyexperiment */
class Experiment {
public:
    Experiment(int argc, char *argv[], PyMethodDef commands[]){
        //std::cout << "Constructor" << std::endl;
        Py_Initialize();
        Py_InitModule("cpp", commands);
        PySys_SetArgvEx(argc, argv, 0); 
        PyRun_SimpleString("import sys; sys.path.append('/home/peter/Dev/python-examples/')");
        PyRun_SimpleString("from pyexperiment.conf import conf");
        PyRun_SimpleString("from pyexperiment.log import log");
        PyRun_SimpleString("from pyexperiment.experiment import init_log");
        PyRun_SimpleString("from pyexperiment import experiment");
        PyRun_SimpleString("import cpp");
        PyRun_SimpleString("commands = [eval(\"cpp.\" + command) for command in dir(cpp) if command[:2] != \"__\"]");
        //PyRun_SimpleString("print(commands)");
        PyRun_SimpleString("experiment.main(commands)");
    }

    ~Experiment(){
        //std::cout << "Deconstructor" << std::endl;
        Py_Finalize();
    }

    void log(std::string message){
        //std::cout << "Log" << std::endl;
        std::string command = "log.error(\"" + message + "\")";
        PyRun_SimpleString(command.c_str());
    }

};

class ExperimentFunction{
public:
    const static std::string docstring;
};
    
const std::string ExperimentFunction::docstring = "Foo bar.";

class Foo : public ExperimentFunction {
public:
    void operator () () { printf("Foo\n"); }
};

std::string hello(char* test){
    std::cout << "Hello from the hello function " + std::string(test) << std::endl;
    return("Hello");
}

static PyObject * hello_wrapper(PyObject * self, PyObject * args)
{
    char * input;
    std::string result;
    PyObject * ret;

    // parse arguments
    if (!PyArg_ParseTuple(args, "s", &input)) {
        return NULL;
    }

    // run the actual function
    result = hello(input);

    // build the resulting string into a Python object.
    ret = PyString_FromString(result.c_str());

    return ret;
}

static PyMethodDef commands[] = {
    {"hello", hello_wrapper, METH_VARARGS, "Say hello"},
    {NULL, NULL, 0, NULL}
};


int main(int argc, char *argv[]) {
    Experiment experiment(argc, argv, commands);
    experiment.log("Hello from here...");

    return 0;
}
