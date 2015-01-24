cmake_minimum_required(VERSION 2.8)

project(pyexperiment-cpp-example)
find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_PATH})
   
add_executable(cpp-example main.cpp)
target_link_libraries(cpp-example ${PYTHON_LIBRARIES})