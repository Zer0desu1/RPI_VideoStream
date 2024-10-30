#include <opencv2/opencv.hpp>
#include <iostream>
#include <string>
#include <unistd.h>
#include <cstdlib>
#include <sstream>
#include <thread>
#include <sys/socket.h>
#include <netinet/in.h>

using namespace cv;
using namespace std;

void start_streaming(VideoCapture &cap, const string &address) {
    // Create a socket
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        cerr << "Error: Could not create socket." << endl;
        return;
    }

    // Define server address
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(8080);

    // Bind the socket
    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        cerr << "Error: Could not bind socket." << endl;
        close(server_fd);
        return;
    }

    // Listen for incoming connections
    listen(server_fd, 1);
    cout << "Listening for connections on " << address << "..." << endl;

    while (true) {
        // Accept a client connection
        int client_fd = accept(server_fd, NULL, NULL);
        if (client_fd < 0) {
            cerr << "Error: Could not accept connection." << endl;
            break;
        }

        cout << "Client connected." << endl;

        // Send HTTP headers
        stringstream response;
        response << "HTTP/1.0 200 OK\r\n"
                 << "Content-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n";

        send(client_fd, response.str().c_str(), response.str().length(), 0);

        // Capture and send frames
        while (true) {
            Mat frame;
            cap >> frame; // Capture frame from camera

            if (frame.empty()) {
                cerr << "Error: Empty frame." << endl;
                break;
            }

            // Encode frame to JPEG
            vector<uchar> buffer;
            imencode(".jpg", frame, buffer);
            string encoded_frame(buffer.begin(), buffer.end());

            // Send frame to client
            stringstream frame_stream;
            frame_stream << "--frame\r\n"
                         << "Content-Type: image/jpeg\r\n"
                         << "Content-Length: " << encoded_frame.size() << "\r\n\r\n"
                         << encoded_frame << "\r\n";
            send(client_fd, frame_stream.str().c_str(), frame_stream.str().length(), 0);

            // Break the loop if the client disconnects
            // You can implement a timeout or other mechanisms for more control
            if (recv(client_fd, nullptr, 0, MSG_DONTWAIT) < 0) {
                break; // Client disconnected
            }
        }

        close(client_fd);
        cout << "Client disconnected." << endl;
    }

    close(server_fd);
}

int main() {
    VideoCapture cap(0); // Open the default camera 
    if (!cap.isOpened()) {
        cerr << "Error: Could not open camera." << endl;
        return -1;
    }

    string address = "http://192.168.1.17:8080/video_feed"; 

    // Start streaming in a separate thread
    thread streaming_thread(start_streaming, ref(cap), address);
    streaming_thread.detach();

    // Keep the main thread alive
    cout << "Press Enter to exit..." << endl;
    cin.get();

    // Release the camera
    cap.release();
    return 0;
}
