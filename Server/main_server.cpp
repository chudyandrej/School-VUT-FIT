
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <sys/socket.h>

#include <netinet/in.h>
#include <vector>
#include <iostream>
#include <arpa/inet.h>

#include "client.h"

#define WELCOME_MSG "Hi, type anything. To end type 'bye.' at a separate line.\n"


bool is_number(const std::string& s);

int main (int argc, const char * argv[]) {
    int welcome_socket;
    struct sockaddr_in6 sa;
    struct sockaddr_in6 sa_client;
    char str[INET6_ADDRSTRLEN];
    std::string::size_type sz;   // alias of size_t
    int servet_port = 0;

    if (argc != 3){
        fprintf(stderr, "Bed count of arguments!");
        return 1;
    }
    if (!std::string(argv[1]).compare(std::string("-p"))){
        if (is_number(std::string(argv[2]))){
            servet_port = std::stoi (std::string(argv[2]),&sz);
        }
    }
    else {
        fprintf(stderr, "Program dont know whot is fleg \"%s\"\n", argv[1]);
        return 1;
    }

    std::vector<Client*> connections;
    socklen_t sa_client_len = sizeof(sa_client);
    if ((welcome_socket = socket(PF_INET6, SOCK_STREAM, 0)) < 0) {
        perror("socket() failed");
        exit(EXIT_FAILURE);
    }

    memset(&sa,0,sizeof(sa));
    sa.sin6_family = AF_INET6;
    sa.sin6_addr = in6addr_any;
    sa.sin6_port = htons(servet_port);
    if ((bind(welcome_socket, (struct sockaddr*)&sa, sizeof(sa))) < 0) {
        perror("bind() failed");
        exit(EXIT_FAILURE);
    }
    if ((listen(welcome_socket, 1)) < 0) {
        perror("listen() failed");
        exit(EXIT_FAILURE);
    }

    while(1) {


        int comm_socket = accept(welcome_socket, (struct sockaddr *) &sa_client, &sa_client_len);
        if (comm_socket <= 0) {
            continue;
        }

        if(inet_ntop(AF_INET6, &sa_client.sin6_addr, str, sizeof(str))) {
            printf("Client address is %s\n",  str);
            printf("Client port is %d\n",  ntohs(sa_client.sin6_port));
        }

        for (size_t i = 0; i < connections.size(); i++) {
            if (connections[i]->isConnection_end()) {
                delete connections[i];
                connections.erase(connections.begin() + i);
            }
        }

        connections.push_back(new Client(comm_socket));


    }
}

bool is_number(const std::string& s)
{
    return !s.empty() && std::find_if(s.begin(),s.end(), [](char c) { return !std::isdigit(c); }) == s.end();
}