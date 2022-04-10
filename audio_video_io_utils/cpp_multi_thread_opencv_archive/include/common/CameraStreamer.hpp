#pragma once
#include "opencv2/videoio.hpp"
#include "tbb/tbb.h"
#include <iostream>
#include <string>
#include <thread>
#include <vector>

class CameraStreamer {
public:
  // this holds camera stream urls
  std::vector<std::string> camera_source;
  // this holds usb camera indices
  std::vector<int> camera_index;
  // this holds OpenCV VideoCapture pointers
  std::vector<cv::VideoCapture *> camera_capture;
  // this holds queue(s) which hold images from each camera
  std::vector<tbb::concurrent_bounded_queue<cv::Mat> *> frame_queue;
  // this holds thread(s) which run the camera capture process
  std::vector<std::thread *> camera_thread;

  // Constructor for IP Camera capture
  CameraStreamer(std::vector<std::string> source);
  // Constructor for USB Camera capture
  CameraStreamer(std::vector<int> index);
  // Destructor for releasing resource(s)
  ~CameraStreamer();

private:
  bool isUSBCamera;
  int camera_count;
  // initialize and start the camera capturing process(es)
  void startMultiCapture();
  // release all camera capture resource(s)
  void stopMultiCapture();
  // main camera capturing process which will be done by the thread(s)
  void captureFrame(int index);
};
