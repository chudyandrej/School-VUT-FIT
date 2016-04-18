//
// Created by Andrej Oliver Chudý on 13/04/16.
//

#include "client.h"



void Client::service_request(std::vector<std::string> request_MSG) {
    if (request_MSG.size() > 0) {
        if (request_MSG[0] == "D" && request_MSG.size() == 2) {
            if (upload(communication_socket,request_MSG[1]) != SUCCS){
                sendMassage(communication_socket,"ERROR");
            }
        }
        else if (request_MSG[0] == "U" && request_MSG.size() == 3 ) {
            if (download(communication_socket, request_MSG[1], request_MSG[2]) != SUCCS) {
                sendMassage(communication_socket,"ERROR");
            }
        }
        else {
            sendMassage(communication_socket,"SYN");
        }
    }
    else{
       sendMassage(communication_socket,"EMP");
    }
}


int Client::download(int socket, std::string filename, std::string str_fileSIZE) {
    char buffer[BUFFER_SIZE];
    long fileSIZE;
    std::vector<std::string> request_summary;
    std::ofstream file;

    sendMassage(socket, "OK");

    fileSIZE = string_to_number(str_fileSIZE);
    file.open(filename, std::ios::binary);

    if( !file.is_open() ){
        perror("Unable to create a file\n ");
        return FAIL;
    }

    printf( "Filename: %s Length:%ld\n" ,filename.c_str(),fileSIZE );     //debug

    int bytes = 0;
    int received = 0;
    while(bytes != fileSIZE) {
        memset(buffer, 0, sizeof(buffer));
        received = (int) recv(socket, buffer, BUFFER_SIZE, 0);
        if (received <= 0) {
            break;
        }
        file.write(buffer, received);
        bytes += received;
    }
    file.close(); //check if successful?

    if(bytes != fileSIZE){
        perror("Error some data was losed");
        return FAIL;
    }
    else{
        return SUCCS;
    }
}

int Client::upload(int socket, std::string filename){
    long sizeFILE;
    char buffer[BUFFER_SIZE];
    std::string str_sizeFILE;
    std::ofstream file; 
    
    sizeFILE = fileSizeFunc(filename);
    if (sizeFILE == -1){
        sendMassage(socket,"NF");
        perror("File problem");
        return FAIL;
    }
    sendMassage(socket,"OK," + number_to_string(sizeFILE));
  
    memset(buffer, 0, sizeof(buffer));
    int upload_file = open(filename.c_str(), O_RDONLY);
    int rc = flock(upload_file, LOCK_SH);
    if (rc){
        sendMassage(socket,"NF");
        perror("File lock problem");
        return FAIL;
    }
    printf("Filename: %s , Length: %ld \n",filename.c_str(),sizeFILE);
    ssize_t bytes_read = 0;
    ssize_t bytes_written = 0; 
    while (1) {
        memset(buffer, 0, sizeof(buffer));
        bytes_read = read(upload_file, buffer, sizeof(buffer));
        if (bytes_read == 0) { break; } //whole file is read
        if (bytes_read < 0) {
            perror("Reading from file FAILED\n");
            return FAIL;
        }

        char *buffPtr = buffer;
        while (bytes_read > 0) {
            bytes_written = write(socket, buffPtr, (size_t) bytes_read);
            if (bytes_written <= 0) {
                perror("Sending bytes FAILED");
                return FAIL;
            }
            bytes_read -= bytes_written;
            buffPtr += bytes_written;
        }
    }

    file.close(); //check if successful?
    return SUCCS;
}


long Client::fileSizeFunc(std::string filename) {
    std::ifstream file;
    file.open(filename, std::ios::binary);
    if(!file){
        return -1; //but file should exists, it's checked in other context
    }
    file.seekg(0, std::ios::end);
    std::streamoff fileSize = file.tellg();
    file.close();
    return fileSize;
}


int  Client::sendMassage(int socket, std::string request) {
    request = request + "\n\n";
    unsigned long requestLen = request.length() + 1;
    const char *c;

    c = request.c_str();
    int sent = 0;
    int bytes = 0;
    while (sent < (int)requestLen){
        bytes = (int) send(socket, c+sent, (size_t) requestLen, 0);
        if (bytes < 0) {
            perror("Sending request FAILED");
            return FAIL;
        }
        if (bytes == 0) {
            break;
        }
        sent += bytes;
    }
    if(sent != (int)requestLen){
        perror("ERROR: NOT entire request sent");
        return FAIL;
    }
    return SUCCS;
}

std::vector<std::string> Client::split(std::string input, char delimiter) {
    std::stringstream stream_massage(input);
    std::string segment;
    std::vector<std::string> seglist;

    while(std::getline(stream_massage, segment, delimiter)) {
        seglist.push_back(segment);
    }
    return seglist;
}

std::string Client::replace_string(std::string input, std::string wanted, std::string for_what){
    size_t f = input.find(wanted);
    input.replace(f, std::string(wanted).length(), for_what);
    return input;
}

std::vector<std::string> Client::load_request(int socket){

    char buffer[BUFFER_SIZE];
    memset(buffer, 0, BUFFER_SIZE);
    std::string massage;
    int received = 0;
   
    while(true){
        received = recv(socket, buffer, (size_t)(BUFFER_SIZE), 0);
        massage = massage + std::string(buffer);
        if (received <= 0) {
            break;
        }

        if(massage.find("\n\n") != std::string::npos){
            massage = replace_string(massage,"\n\n","");
            break;
        }
    }
    return split(massage,',');
}


long Client::string_to_number(std::string input){
    long output;
    try {
        std::istringstream (input) >>  output; 
    }
    catch(...) {
        perror("Error during converting string to number");
        exit(FAIL);
    }
    return output;
}

std::string Client::number_to_string(long input){
    std::ostringstream stream_to_str;
    try {
        stream_to_str << input; 
    }
    catch(...) {
        perror("Error during converting number to string");
        exit(FAIL);
    }
    return stream_to_str.str();
}
