#include <Python.h>
#include <iostream>

int main() {
    // Initialize Python
    Py_Initialize();

    if (!Py_IsInitialized()) {
        std::cerr << "❌ Failed to initialize Python interpreter\n";
        return 1;
    }

    try {
        // Add project path to sys.path
        PyRun_SimpleString("import sys");
        PyRun_SimpleString("sys.path.append('.')");

        // Optionally: import a specific test runner
        PyObject* module_name = PyUnicode_FromString("nes_container_manager.tests.run_test");
        PyObject* module = PyImport_Import(module_name);
        Py_DECREF(module_name);

        if (!module) {
            PyErr_Print();
            std::cerr << "❌ Failed to import Python test module\n";
            return 1;
        }

        // Optionally: call a function (if you expose one in run_test.py)
        // Example:
        // PyObject* func = PyObject_GetAttrString(module, "run_test");
        // if (PyCallable_Check(func)) PyObject_CallObject(func, NULL);

        Py_DECREF(module);

    } catch (...) {
        std::cerr << "❌ Exception occurred while running embedded Python\n";
    }

    // Finalize Python
    Py_Finalize();
    return 0;
}
