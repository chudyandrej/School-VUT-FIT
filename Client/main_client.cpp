#include <iostream>
#include <getopt.h>
#include <sys/socket.h>
#include <netdb.h>
#include <sstream>
#include <vector>
#include <fstream>

#define BUFFER_SIZE 1024

using namespace std;

std::tuple<int, string, string,string> arguments_process(int argc, char *argv[]);
int create_connection(string host_srver, int port);
int sendRequest(int socket, string request);
void make_request_to_server(int socket, string download_path, string upload_path);
std::vector<std::string> respond(int socket);
int download(int socket_desc, std::string filename);
long fileSizeFunc(std::string filename);


int main(int argc, char *argv[]) {
    int socket,port;
  
    string host, download_path,upload_path;
    std::tie(port, host, download_path, upload_path) = arguments_process(argc, argv);
    socket = create_connection(host, port);
   // sendRequest(socket, string("seifaekughkseighkweugh"));
    make_request_to_server(socket,download_path, upload_path);


    close(socket);

    return EXIT_SUCCESS;
}

std::tuple<int, string, string,string> arguments_process(int argc, char *argv[]) {

    int argFleg, port = 0;
    string host, download_path, upload_path;

    while ((argFleg = getopt(argc, argv, "p:h:d:u:")) != -1) {
        switch (argFleg) {
            case 'p':
                try {
                    port = stoi(optarg);
                }
                catch(...) {
                    cerr << "Port must be number" << endl;
                    return EXIT_FAILURE;
                }
                break;
            case 'h':
                host = optarg;
                break;
            case 'd':
                download_path = optarg;
                break;
            case 'u':
                upload_path = optarg;
                break;
            default:
                throw std::invalid_argument(optarg);
        }
    }
    if ((!port || host.empty()) || !(download_path.empty() ^ upload_path.empty())){
        cerr << "Invalid combination of arguments" << endl;
        exit(6);
    }
    return std::make_tuple(port,host, download_path, upload_path);
}


int create_connection(string host_server, int port){
  
    int client_socket = 0;
    struct sockaddr_in server_address;
    struct hostent *host;
    std::string copy_url = host_server;
    if ((host= gethostbyname(copy_url.c_str())) == NULL){
        fprintf(stderr, "Error: Bed format of URL!\n");
        exit(EXIT_FAILURE);
    }

    if ((client_socket = socket(AF_INET, SOCK_STREAM, 0)) <= 0) {
        fprintf(stderr, "Error: Unsucessful creat socet\n");
        exit(EXIT_FAILURE);
    }
    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(port);
    server_address.sin_addr = *((struct in_addr *)host->h_addr);
    memset(server_address.sin_zero, '\0', sizeof server_address.sin_zero);

    if (connect(client_socket, (const struct sockaddr *) &server_address, sizeof(server_address)) != 0) {
        fprintf(stderr, "Error: Unsucessful connection to server\n");
        exit(EXIT_FAILURE);
    }
    return client_socket;
}

void make_request_to_server(int socket, string download_path, string upload_path) {
    std::string request;
    char server_mesg[5];
    if (!download_path.empty()) {
        request = "D," + download_path + "\n\n";
        printf ("%s",request.c_str());
        sendRequest(socket, request);
        download(socket , download_path);

    }
    else if (!upload_path.empty()) {
        request = "U," + upload_path + "\n\n";
        sendRequest(socket, request);
    }
    else {
        cerr << "Fatal ERROR" << endl;
        exit(6);
    }

   recv(socket, server_mesg, sizeof(server_mesg), 0);
   printf("%s", server_mesg);

}


int sendRequest(int socket, string request) {

    unsigned long requestLen = request.length()+1;
    const char *c;

    c = request.c_str();
    int sent = 0;
    int bytes = 0;
    while (sent < (int)requestLen){
        bytes = (int) send(socket, c+sent, (size_t) requestLen, 0);
        if (bytes < 0) {
            cerr << "Sending request FAILED" << endl;
            return EXIT_FAILURE;
        }
        if (bytes == 0) {
            break;
        }
        sent += bytes;
    }
    if(sent != (int)requestLen){
        cerr << "ERROR: NOT entire request sent" << endl;
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}

std::vector<std::string> split(std::string input, char delimiter) {
    std::stringstream stream_massage(input);
    std::string segment;
    std::vector<std::string> seglist;

    while(std::getline(stream_massage, segment, delimiter)) {
        seglist.push_back(segment);
    }
    return seglist;
}




int download(int socket_desc, std::string filename) {
    char buffer[BUFFER_SIZE];
    long sizeFILE;
    std::vector<std::string> respond_summary;
    printf("cakam\n");
    respond_summary = respond(socket_desc);
    printf("pokracujem\n");
    if(respond_summary[0].compare("CLS") && respond_summary.size() != 2){
        perror("Bed syntax of request, server don't understood");
        exit(11);
    }
    else if(respond_summary[0].compare("NF") && respond_summary.size() != 2){
        perror("No such file or directory on server");
        exit(12);
    }
    else if(respond_summary[0].compare("EMP")){
        perror("Something is wrong sanded request was empty");
        exit(13);
    }

    try {
        sizeFILE = stoi(respond_summary[1]);
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

void upload(int socket, std::string filename){

    int bytes = 0;
    int received;
    long sizeFILE;
    char buffer[BUFFER_SIZE];
    long dataLength;
    size_t index;
    size_t end;
    std::ofstream file; //has automatically ios::out flag
    std::string request;

    sizeFILE =  fileSizeFunc(filename);
    request = "OK," + sizeFILE;
    send(socket, request.c_str(), sizeof(request), 0);

    memset(buffer, 0, sizeof(buffer));
    file.open(filename, std::ios::binary);
    //cout << "Filename:" << filename << "\nLength:" << dataLength << endl; //debug

    while(bytes != dataLength) {
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
    /*if(bytes == dataLength){ sendResponse(comm_socket, ACK, ""); }
    else{ sendResponse(comm_socket, NACK, ""); } //delete created file??*/

}


long fileSizeFunc(std::string filename) {

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
std::vector<std::string> respond(int socket){
    char buffer[BUFFER_SIZE];
    memset(buffer, 0, BUFFER_SIZE);
    std::string massage;

    while(recv(socket, buffer, (size_t)(BUFFER_SIZE), 0) > 0){
        massage.append(buffer);
        if(massage.find("\n\n") != std::string::npos){
            break;
        }
    }
    return split(massage,',');
}