//
// Created by Andrej Oliver Chudý on 13/04/16.
//


#include "client.h"



void Client::comunication() {
    send(communication_socket, WELCOME_MSG, strlen(WELCOME_MSG), 0);
    char buff[1024];
    receiveReq(communication_socket, buff);
    printf("Connection to  closed\n");
    close(communication_socket);
    connection_end = true;

}

 Client::receiveReq(int socket, char *buffer) {
    memset(buffer, 0, 1024);
    int received = 0;
    int total = 0;

    while(true){
        received =(int) recv(socket, buffer + total, (size_t)(1024 - total), 0);
        std::string str(buffer);

        if (received <= 0){
            break;
        }
        total += received;

    }
    return 1;

}

