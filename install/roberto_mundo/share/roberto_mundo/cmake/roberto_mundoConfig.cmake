# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_roberto_mundo_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED roberto_mundo_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(roberto_mundo_FOUND FALSE)
  elseif(NOT roberto_mundo_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(roberto_mundo_FOUND FALSE)
  endif()
  return()
endif()
set(_roberto_mundo_CONFIG_INCLUDED TRUE)

# output package information
if(NOT roberto_mundo_FIND_QUIETLY)
  message(STATUS "Found roberto_mundo: 2.3.7 (${roberto_mundo_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'roberto_mundo' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT roberto_mundo_DEPRECATED_QUIET)
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(roberto_mundo_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "ament_cmake_export_include_directories-extras.cmake;ament_cmake_export_dependencies-extras.cmake")
foreach(_extra ${_extras})
  include("${roberto_mundo_DIR}/${_extra}")
endforeach()
