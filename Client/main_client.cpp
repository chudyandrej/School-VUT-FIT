#include <iostream>
#include <getopt.h>
#include <sys/socket.h>
#include <vector>
#include <string.h>
#include <netinet/in.h>
#include <fstream>
#include <arpa/inet.h> //inet_addr
#include <fcntl.h>
#include <unistd.h>
#include <sstream>
#include <netdb.h> //gethostbyname
#include <iostream>
#include <set>
#include <tuple>
#include <stdlib.h>  


#define BUFFER_SIZE 1024

#define FATAL_ERROR 9
#define FAIL_CONNECTION 2
#define FAIL_FILE 3
#define FAIL_TRANS 5
#define FAIL 1
#define SUCCS 0

using namespace std;

std::string number_to_string(long input);
long string_to_number(std::string input);
std::tuple<int, string, string,string> arguments_process(int argc, char *argv[]);
int create_connection(string host_srver, int port);
int sendRequest(int socket, string request);
void make_request_to_server(int socket, string download_path, string upload_path);
std::vector<std::string> respond(int socket);
int download(int socket, std::string fileName);
int upload(int socket, std::string fileName);
long fileSizeFunc(std::string fileName);
void chack_respond_status(std::string respond_status);
std::string replace_string(std::string input, std::string wanted, std::string for_what);


int main(int argc, char *argv[]) {
    int socket,port;
  
    string host, download_path,upload_path;
    std::tie(port, host, download_path, upload_path) = arguments_process(argc, argv);
    socket = create_connection(host, port);
  
    if (!download_path.empty()){
        return download(socket , download_path);
    }
    else if (!upload_path.empty()) {
        return upload(socket, upload_path);
    }
    else {
        perror( "Fatal ERROR\n" );
        return FATAL_ERROR;
    }
    close(socket);

    return SUCCS;
}

std::tuple<int, string, string,string> arguments_process(int argc, char *argv[]) {

    int argFleg, port = 0;
    string host, download_path, upload_path;

    while ((argFleg = getopt(argc, argv, "p:h:d:u:")) != -1) {
        switch (argFleg) {
            case 'p':
                try {
                     std::istringstream (optarg) >>  port ;               
                }
                catch(...) {
                    cerr << "Port must be number" << endl;
                    exit(FAIL);
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
    return std::make_tuple(port,host, download_path, upload_path);  //ok
}

int create_connection(string host_server, int port){
   
    struct sockaddr_in addr;
    struct hostent *server = NULL;

    int client_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (client_socket <= 0){
        fprintf(stderr, "Error: Unsucessful creat socet\n");
        exit(FAIL_CONNECTION);
    }

    //domain name to ip address
    server = gethostbyname(host_server.c_str());
    if (server == NULL){
        exit (FAIL_CONNECTION);
    }
    //fill structure for connect()
    memset(&addr,0,sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    memcpy(&addr.sin_addr.s_addr, server->h_addr_list[0], (size_t)server->h_length);
    //Create connection
    if((connect( client_socket, (struct sockaddr*) &addr, sizeof(addr) )) < 0){
        cerr << "Unable to connect" << endl;
        exit (FAIL_CONNECTION);
    }
    return client_socket;    //ok
}
   
int download(int socket, std::string fileName) {
   
    char buffer[BUFFER_SIZE];
    long sizeFILE;
    std::vector<std::string> respond_vector;
    
    if (sendRequest(socket, "D," + fileName) == FAIL_TRANS){return FAIL_TRANS;}     // send reques to server: "D,fileName\n\n"
    respond_vector = respond(socket);                                   // wait antil server send respond
    chack_respond_status(respond_vector[0]);                            // chack if server respod was "ok"

    sizeFILE = string_to_number(respond_vector[1]);                     //in respond is on second position file size
   
    std::ofstream file;     
    file.open(fileName, std::ios::binary);                              //open file to write
    if( !file.is_open() ){
        perror("Unable to create a file\n");
        return (FAIL_FILE);
    }
    printf( "fileName: %s Length:%ld\n" ,fileName.c_str(),sizeFILE );     //debug

    int bytes = 0;
    int received = 0;
    while(bytes != sizeFILE) {                              //start downloading data
        memset(buffer, 0, sizeof(buffer));
        received = (int) recv(socket, buffer, BUFFER_SIZE, 0);          
      
        if (received <= 0) {
            break;
        }
        file.write(buffer, received);
        bytes += received;
    }
   
    file.close();
    if(bytes != sizeFILE){
        perror("Error some data was losed");
        return FAIL_TRANS;
    }
    else{
        printf("SUCESS !!!!!!!!\n");
        return SUCCS;
    } //ok
}

int upload(int socket, std::string fileName){

    long sizeFILE;
    char buffer[BUFFER_SIZE];
    std::vector<std::string> respond_vector;
    std::ofstream file; 
    std::string request;

    sizeFILE = fileSizeFunc(fileName);
    if (sizeFILE == -1){
        perror("File not found\n");
        exit(FAIL_FILE);
    }
   
    if (sendRequest(socket, "U," +fileName+","+ number_to_string(sizeFILE)) == FAIL_TRANS){return FAIL_TRANS;}    //send reqest "U,fileName,size\n\n"
    respond_vector = respond(socket);                               
    chack_respond_status(respond_vector[0]);                    //chcek respond
    
    memset(buffer, 0, sizeof(buffer));
    int upload_file = open(fileName.c_str(), O_RDONLY);
    printf("fileName: %s , Length: %ld \n",fileName.c_str(),sizeFILE);
    ssize_t bytes_read = 0;
    ssize_t bytes_written = 0; 
    while (1) {
        memset(buffer, 0, sizeof(buffer));
        bytes_read = read(upload_file, buffer, sizeof(buffer));
        if (bytes_read == 0) { break; } //whole file is read
        if (bytes_read < 0) {
            perror("Reading from file FAILED\n");
            return FAIL_FILE;
        }
        char *buffPtr = buffer;
        while (bytes_read > 0) {
            bytes_written = write(socket, buffPtr, (size_t) bytes_read);
            if (bytes_written <= 0) {
                printf("Sending bytes FAILED");
                return FAIL_TRANS;
            }
            bytes_read -= bytes_written;
            buffPtr += bytes_written;
        }
    }
    printf("SUCCESS !!!!!!!\n");
    file.close(); //check if successful?
    return SUCCS; //ok
}

int sendRequest(int socket, string request) {
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
            return FAIL_TRANS;
        }
        if (bytes == 0) {
            break;
        }
        sent += bytes;
    }
    if(sent != (int)requestLen){
        perror("ERROR: NOT entire request sent");
        return FAIL_TRANS;
    }
    return SUCCS;
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

long string_to_number(std::string input){
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

std::string number_to_string(long input){
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

long fileSizeFunc(std::string fileName) {

    std::ifstream file;
    file.open(fileName, std::ios::binary);
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
    int received = 0;
   
    while(true){
        received = recv(socket, buffer, (size_t)(BUFFER_SIZE), 0);
        massage = massage + string(buffer);
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

void chack_respond_status(std::string respond_status){
    if(respond_status == "CLS" ){
        perror("Bed syntax of request, server don't understood");
        exit(11);
    }
    else if(respond_status == "NF"){
        perror("No such file or directory on server");
        exit(12);
    }
    else if(respond_status == "EMP"){
        perror("Something is wrong sanded request was empty");
        exit(13);
    }
    else if (respond_status != "OK"){
        perror("Something is wrong");
        exit(13);
    }
}

std::string replace_string(std::string input, std::string wanted, std::string for_what){
    size_t f = input.find(wanted);
    input.replace(f, std::string(wanted).length(), for_what);
    return input;
}





