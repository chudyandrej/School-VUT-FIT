//
// Created by Andrej Oliver Chudý on 11/04/16.
//

#ifndef SERVER_CLIENT_H
#define SERVER_CLIENT_H


#include <thread>
#include <zconf.h>
#include <sys/socket.h>
#include <string>
#include <fstream>
#include <unistd.h>
#include <vector>
#include <cstdlib>
#include <stdio.h>
#include <iostream>
#include <stdlib.h>
#include <string.h>
#include <sstream>
#include <fcntl.h>
#include <sys/file.h>


#define BUFFER_SIZE 1024
#define SUCCS 0
#define FAIL 1


class Client {

private:

    bool connection_end ;
    int communication_socket;
    std::thread thread_;


    void service_request(std::vector<std::string> request_MSG) ;
    void upload(int socket, std::string filename);
    void download(int socket_desc, std::string filename, std::string str_fileSIZE);

    int sendMessage(int socket, std::string request) ;

    long fileSizeFunc(std::string filename);
    long string_to_number(std::string input);

    std::string number_to_string(long input);
    std::vector<std::string> load_request(int socket);
    std::vector<std::string> split(std::string input, char delimiter);
    std::string replace_string(std::string input, std::string wanted, std::string for_what);


    
    void  comunication(){
        service_request(  load_request(communication_socket)  );
        connection_end = true;
        close(communication_socket);
    }



public:
    //constructor
    Client(int comm_socket){
        connection_end = false;
        communication_socket = comm_socket;
        thread_ = std::thread(&Client::comunication,this);

    }
    //destructor
    virtual ~Client() {
        if (thread_.joinable()) thread_.join();
    }

    bool isConnection_end() const {
        return connection_end;
    }
};

#endif //SERVER_CLIENT_H
