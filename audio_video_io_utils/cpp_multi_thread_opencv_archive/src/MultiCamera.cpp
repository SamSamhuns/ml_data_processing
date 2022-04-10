#include "CameraStreamer.hpp"
#include "opencv2/highgui.hpp"

int main() {

  // IP camera URLs
  std::vector<std::string> capture_source = {
      "rtsp://192.168.2.100/profile2/media.smp",
      "rtsp://192.168.0.100/profile2/media.smp"};

  // USB Camera indices
  std::vector<int> capture_index = {0, 1};

  // Highgui window titles
  std::vector<std::string> label;
  for (int i = 0; i < capture_source.size(); i++) {
    std::string title = "CCTV " + std::to_string(i);
    label.push_back(title);
  }

  // Make an instance of CameraStreamer
  CameraStreamer cam(capture_source);

  while (cv::waitKey(20) != 27) {
    // Retrieve frames from each camera capture thread
    for (int i = 0; i < capture_source.size(); i++) {
      cv::Mat frame;
      // Pop frame from queue and check if the frame is valid
      if (cam.frame_queue[i]->try_pop(frame)) {
        // Show frame on Highgui window
        cv::imshow(label[i], frame);
      }
    }
  }
  return 0;
}
