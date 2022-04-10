#include "CameraStreamer.hpp"

CameraStreamer::CameraStreamer(std::vector<std::string> stream_source) {
  camera_source = stream_source;
  camera_count = camera_source.size();
  isUSBCamera = false;

  startMultiCapture();
}

CameraStreamer::CameraStreamer(std::vector<int> capture_index) {
  camera_index = capture_index;
  camera_count = capture_index.size();
  isUSBCamera = true;

  startMultiCapture();
}

CameraStreamer::~CameraStreamer() { stopMultiCapture(); }

void CameraStreamer::captureFrame(int index) {
  cv::VideoCapture *capture = camera_capture[index];
  while (true) {
    cv::Mat frame;
    // Grab frame from camera capture
    (*capture) >> frame;
    // Put frame to the queue
    frame_queue[index]->try_push(frame);
    // relase frame resource
    frame.release();
  }
}

void CameraStreamer::startMultiCapture() {
  cv::VideoCapture *capture;
  std::thread *t;
  tbb::concurrent_bounded_queue<cv::Mat> *q;
  for (int i = 0; i < camera_count; i++) {
    // Make VideoCapture instance
    if (!isUSBCamera) {
      std::string url = camera_source[i];
      capture = new cv::VideoCapture(url);
      std::cout << "Camera Setup: " << url << std::endl;
    } else {
      int idx = camera_index[i];
      capture = new cv::VideoCapture(idx);
      std::cout << "Camera Setup: " << std::to_string(idx) << std::endl;
    }

    // Put VideoCapture to the vector
    camera_capture.push_back(capture);

    // Make thread instance
    t = new std::thread(&CameraStreamer::captureFrame, this, i);

    // Put thread to the vector
    camera_thread.push_back(t);

    // Make a queue instance
    q = new tbb::concurrent_bounded_queue<cv::Mat>;
    // set capacity for queue to prevent producer overflow
    // set queue capacity to a lower number
    q->set_capacity(2);

    // Put queue to the vector
    frame_queue.push_back(q);
  }
}

void CameraStreamer::stopMultiCapture() {
  cv::VideoCapture *cap;
  for (int i = 0; i < camera_count; i++) {
    cap = camera_capture[i];
    if (cap->isOpened()) {
      // Relase VideoCapture resource
      cap->release();
      std::cout << "Capture " << i << " released" << std::endl;
    }
  }
}
