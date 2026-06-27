# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_zenpool_draw_letter_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED zenpool_draw_letter_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(zenpool_draw_letter_FOUND FALSE)
  elseif(NOT zenpool_draw_letter_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(zenpool_draw_letter_FOUND FALSE)
  endif()
  return()
endif()
set(_zenpool_draw_letter_CONFIG_INCLUDED TRUE)

# output package information
if(NOT zenpool_draw_letter_FIND_QUIETLY)
  message(STATUS "Found zenpool_draw_letter: 0.0.0 (${zenpool_draw_letter_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'zenpool_draw_letter' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT ${zenpool_draw_letter_DEPRECATED_QUIET})
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(zenpool_draw_letter_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${zenpool_draw_letter_DIR}/${_extra}")
endforeach()
