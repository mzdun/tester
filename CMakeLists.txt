# Copyright (c) 2025 Marcin Zdun
# This file is licensed under MIT license (see LICENSE for details)

cmake_minimum_required (VERSION 3.28)
project (tester
  VERSION 1.0.0
  DESCRIPTION ""
  LANGUAGES CXX)

set(PROJECT_VERSION_SHORT "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}")
set(PROJECT_VERSION_STABILITY "" # or "-alpha", or "-beta", or "-rc.1", or "-rc.2"
    CACHE STRING "" FORCE)

if (${CMAKE_CURRENT_SOURCE_DIR} STREQUAL ${CMAKE_CURRENT_BINARY_DIR})
  message(FATAL_ERROR "Building in source firectory is not supported")
endif()

set(TESTER_TESTING ON CACHE BOOL "Compile and/or run self-tests")
set(TESTER_INSTALL ON CACHE BOOL "Install the application")
set(TESTER_SANITIZE OFF CACHE BOOL "Compile with sanitizers enabled")

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_EXTENSIONS OFF)

set_property(GLOBAL PROPERTY USE_FOLDERS ON)

list(APPEND CMAKE_MODULE_PATH "${PROJECT_BINARY_DIR}/conan" "${PROJECT_SOURCE_DIR}/.flow/cmake")
list(APPEND CMAKE_PREFIX_PATH "${PROJECT_BINARY_DIR}/conan")

include(common)
include(output_dirs_setup)

set(CONAN_CMAKE_SILENT_OUTPUT ON)
find_package(Python3 COMPONENTS Interpreter REQUIRED)
find_package(fmt REQUIRED)
find_package(GTest REQUIRED)
find_package(mbits-args REQUIRED)

if (TESTER_TESTING)
  enable_testing()

  find_package(GTest REQUIRED)

  set(TEST_REPORT_DIR "${PROJECT_BINARY_DIR}/test-results")
  set(TEST_SANITIZER_TAG "")
  if (TESTER_SANITIZE)
    set(TEST_SANITIZER_TAG "-sanitizer")
  endif()
  set(TEST_REPORT_FILE "${CMAKE_SYSTEM_NAME}-${CMAKE_CXX_COMPILER_ID}-${CMAKE_BUILD_TYPE}${TEST_SANITIZER_TAG}.xml")
endif()

include(output_dirs_setup)
old_conan_output_dirs_setup()

# See <https://github.com/lefticus/cppbestpractices/blob/v1.0.0/02-Use_the_Tools_Available.md#compilers>

if (MSVC)
  set(TESTER_ADDITIONAL_COMPILE_FLAGS
    /D_CRT_SECURE_NO_WARNINGS
    /D_CRT_NONSTDC_NO_WARNINGS
    /utf-8
    /permissive-
    /Zc:__cplusplus
    /W4
    /w14242
    /w14254
    /w14263
    /w14265
    /w14287
    /we4289
    /w14296
    /w14311
    /w14545
    /w14546
    /w14547
    /w14549
    /w14555
    /w14619
    /w14640
    /w14826
    /w14905
    /w14906
    /w14928
    /w14946)
  if (TESTER_SANITIZE)
    list(APPEND TESTER_ADDITIONAL_COMPILE_FLAGS
      /fsanitize=address
      /D_DISABLE_VECTOR_ANNOTATION
      /D_DISABLE_STRING_ANNOTATION
    )
  endif()
else()
  set(TESTER_ADDITIONAL_COMPILE_FLAGS
      -Wall -Wextra
      -Wnon-virtual-dtor
      -Wold-style-cast
      -Wcast-align
      -Wunused
      -Woverloaded-virtual
      -Wpedantic
      -Wconversion
      -Wsign-conversion
      -Wnull-dereference
      -Wdouble-promotion
      -Wformat=2
  )
  if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
    list(APPEND TESTER_ADDITIONAL_COMPILE_FLAGS
      -fcolor-diagnostics
      -Wno-braced-scalar-init
    # -Wlifetime
    )
  else()
    list(APPEND TESTER_ADDITIONAL_COMPILE_FLAGS
      -fdiagnostics-color
      -Wmisleading-indentation
      -Wduplicated-cond
      -Wduplicated-branches
      -Wlogical-op
      -Wuseless-cast
      )
  endif()
  if (TESTER_SANITIZE)
    list(APPEND TESTER_ADDITIONAL_COMPILE_FLAGS
      -fsanitize=address
      -fsanitize=undefined

    )
    list(APPEND TESTER_ADDITIONAL_LINK_FLAGS
      -fsanitize=address
      -fsanitize=undefined
    )
  endif()
endif()

include(${PROJECT_SOURCE_DIR}/.flow/packages/config.cmake)
include(CPack)

configure_file(src/version.hpp.in include/tester/version.hpp @ONLY)

set(SRCS
  src/main.cpp
  "${CMAKE_CURRENT_BINARY_DIR}/include/tester/version.hpp"
)

add_executable(${PROJECT_NAME} ${SRCS})

add_win32_icon(${PROJECT_NAME} "appicon.ico")
target_compile_options(${PROJECT_NAME} PRIVATE ${TESTER_ADDITIONAL_COMPILE_FLAGS})
target_link_options(${PROJECT_NAME} PUBLIC ${TESTER_ADDITIONAL_LINK_FLAGS})
target_include_directories(${PROJECT_NAME}
  PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_BINARY_DIR}/include
  PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_BINARY_DIR}/src
)
target_link_libraries(${PROJECT_NAME} fmt::fmt mbits::args)
set_target_properties(${PROJECT_NAME} PROPERTIES
  VERSION ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
)

##################################################################
##  INSTALL
##################################################################

if (TESTER_INSTALL)
  install(TARGETS ${PROJECT_NAME})
endif()

##################################################################
##  TESTING
##################################################################

if (TESTER_TESTING)
  file(GLOB EXCLUDES_TEST_SRCS_CC tests/*.cc)
  file(GLOB EXCLUDES_TEST_SRCS_CPP tests/*.cpp)
  file(GLOB EXCLUDES_TEST_SRCS_CXX tests/*.cxx)
  source_group(TREE ${CMAKE_CURRENT_SOURCE_DIR}/tests FILES
    ${EXCLUDES_TEST_SRCS_CC}
    ${EXCLUDES_TEST_SRCS_CPP}
    ${EXCLUDES_TEST_SRCS_CXX})

  add_project_test(${PROJECT_NAME} ${EXCLUDES_TEST_SRCS_CC} ${EXCLUDES_TEST_SRCS_CPP} ${EXCLUDES_TEST_SRCS_CXX})
  target_link_libraries(${PROJECT_NAME}-test PUBLIC GTest::gmock_main fmt::fmt)

  add_test(NAME ${PROJECT_NAME} COMMAND ${PROJECT_NAME}-test "--gtest_output=xml:${TEST_REPORT_DIR}/${PROJECT_NAME}/${TEST_REPORT_FILE}")
endif()
