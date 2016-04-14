//
// Created by Andrej Oliver Chudý on 11/04/16.
//

#ifndef SERVER_CLIENT_H
#define SERVER_CLIENT_H

#define WELCOME_MSG "Hi, type anything. To end type 'bye.' at a separate line.\n"
#include <thread>
#include <zconf.h>
#include <sys/socket.h>
#include <string>
#include <fstream>
#include <cstdlib>
#include <stdio.h>
#include <iostream>
#include <stdlib.h>
#include <string.h>

class Client {

private:

    bool connection_end ;
    int communication_socket;
    std::thread thread_;
    void receiveReq(int socket);
    std::vector<std::string> split_MSG(std::string input,  char delimiter );
    int download(int socket_desc, std::string filename, std::string  fileSize );
    void upload(int comm_socket, std::string filename);
    std::ifstream::pos_type filesize(const char* filename);


public:
    //constructor
    Client(int comm_socket){
        connection_end = false;
        communication_socket = comm_socket;
        thread_ = std::thread(&Client::comunication,this);

    }
    //destructor
    virtual ~Client() {
        close(communication_socket);
        if (thread_.joinable()) thread_.join();
    }

    void  comunication();


    bool isConnection_end() const {
        return connection_end;
    }


private:


};









#endif //SERVER_CLIENT_H
