//
// Created by Andrej Oliver Chudý on 13/04/16.
//


#include <vector>
#include <sstream>
#include <fstream>
#include <sys/stat.h>

#include "client.h"
#define BUFFER_SIZE 1024


void Client::comunication() {

    receiveReq(communication_socket);
    connection_end = true;

}


void Client::receiveReq(int socket) {
    char buffer[BUFFER_SIZE];
    std::vector<std::string> vector_massage;
    memset(buffer, 0, BUFFER_SIZE);
    std::string massage;

    while(recv(socket, buffer, (size_t)(BUFFER_SIZE), 0) > 0){
        massage.append(buffer);
        if(massage.find("\n\n") != std::string::npos){
            break;
        }
    }
    printf("%s\n",massage.c_str());
    if (!massage.empty()) {
        vector_massage = split_MSG(massage, ',');
        printf("%s\n",vector_massage[0].c_str());
        if (!vector_massage[0].compare("D")) {

            printf("UPLOAD\n");
            upload(socket,vector_massage[1]);
        }
        else if (!vector_massage[0].compare("U") ) {
            printf("DOWNLAD\n");
            //send(socket, "OK", sizeof("OK"), 0);
            //download(socket, vector_massage[1], vector_massage[2]);
        }
        else {
            send(socket, "SYN", sizeof("OK"), 0);
        }
    }
    else{
        send(socket, "EMP", sizeof("OK"), 0);
    }
}



std::vector<std::string> Client::split_MSG(std::string input, char delimiter) {
    std::stringstream stream_massage(input);
    std::string segment;
    std::vector<std::string> seglist;

    while(std::getline(stream_massage, segment, delimiter)) {
        seglist.push_back(segment);
    }
    return seglist;
}





int Client::download(int socket_desc, std::string filename, std::string  str_fileSize) {
    char buffer[BUFFER_SIZE];
    long sizeFILE;
    try {
        sizeFILE = stoi(str_fileSize);
    }
    catch(...) {
        //cerr << "Port must be number" << endl;
        return EXIT_FAILURE;
    }

    //receive file itself
    std::ofstream file; //has automatically ios::out flag
    file.open(filename, std::ios::binary);
    if( !file.is_open() ){
        //cerr << "Unable to create a file" << endl;
        return EXIT_FAILURE;
    }
    //cout << "Filename:" << filename << "\nLength:" << fileSize << endl;     //debug

    int bytes = 0;
    int received = 0;
    while(bytes != sizeFILE) {
        memset(buffer, 0, sizeof(buffer));
        received = (int) recv(socket_desc, buffer, BUFFER_SIZE, 0);
        //cout << "something receiving: " <<received << endl; //debug
        if (received <= 0) {
            break;
        }
        file.write(buffer, received);
        bytes += received;
    }

    file.close(); //check if successful?
    if(bytes != sizeFILE){
        //cerr << "Downloading FAILED, NOT entire file was downloaded" << endl;
        return EXIT_FAILURE;
    }
    else{
        //cout << "Downloading completed successfully" << endl;
        return EXIT_SUCCESS;
    }
}

void Client::upload(int socket, std::string filename){

    int bytes = 0;
    int received;
    long sizeFILE;
    char buffer[BUFFER_SIZE];

    std::ofstream file; //has automatically ios::out flag
    std::string request;
    printf("FileName:%s\n", filename.c_str());
    sizeFILE =  filesize(filename.c_str());
    if (sizeFILE == -1){
        printf("File not found\n");
        request = "NF," + std::to_string(sizeFILE);
        send(socket, request.c_str(), sizeof(request), 0);
    }
    std::cout<< sizeFILE<<"\n";
    request = "OK," + std::to_string(sizeFILE);
    printf("req : %s\n",request.c_str() );
    send(socket, request.c_str(), sizeof(request), 0);

    memset(buffer, 0, sizeof(buffer));

    file.open(filename, std::ios::binary);
    //cout << "Filename:" << filename << "\nLength:" << dataLength << endl; //debug

    while(bytes != sizeFILE) {
        received = (int) recv(socket, buffer, sizeof(buffer), 0);
        //cout << "something receiving: " <<received << endl; //debug
        if (received <= 0) {
            break;
        }
        file << buffer;
        memset(buffer, 0, sizeof(buffer));
        bytes += received;
    }

    file.close(); //check if successful?
    //if(bytes == dataLength){ sendResponse(comm_socket, ACK, ""); }
 //   else{ sendResponse(comm_socket, NACK, ""); } //delete created file??

}



std::ifstream::pos_type Client::filesize(const char* filename)
{
    std::ifstream in(filename, std::ifstream::ate | std::ifstream::binary);
    return in.tellg();
}