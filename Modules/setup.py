from setuptools import setup, Extension

module = Extension(
    "hellomodule",  # Must match PyInit_<name> in your .c file
    sources=["hellomodule.c"],
)

setup(
    name="hellomodule",
    version="1.0",
    description="A simple Hello World C extension for Python",
    ext_modules=[module],
)
