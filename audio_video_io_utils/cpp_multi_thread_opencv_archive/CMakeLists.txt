cmake_minimum_required(VERSION 3.20)

project("opencv_multiple")

set(CMAKE_CXX_STANDARD 17)
set(CPP_SOURCES
  "src/CameraStreamer.cpp"
  "src/MultiCamera.cpp")

# get opencv lib
find_package(OpenCV REQUIRED)
# get intels multi-threading lib
find_package(TBB REQUIRED)

add_executable(${PROJECT_NAME}
  ${CPP_SOURCES})

# add include dirs with common header
target_include_directories(${PROJECT_NAME} PRIVATE
  "include/common")

target_link_libraries(${PROJECT_NAME}
  ${OpenCV_LIBS}
  TBB::tbb)
