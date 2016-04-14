#include <iostream>
#include <getopt.h>
#include <sys/socket.h>
#include <netdb.h>



using namespace std;

std::tuple<int, string, string,string> arguments_process(int argc, char *argv[]);
int create_conection(string host_srver, int port);
int sendRequest(int socket, string request);


int main(int argc, char *argv[]) {
    int socket,port;
    string host, download_path,upload_path;
    std::tie(port, host, download_path, upload_path) = arguments_process(argc, argv);

    socket = create_conection(host, port);
    sendRequest(socket, string("ahoj")) ;
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
                throw std::invalid_argument("id");
        }
    }
    if ((!port || host.empty()) || !(download_path.empty() ^ upload_path.empty())){
        throw std::invalid_argument("id");
    }
    return std::make_tuple(port,host, download_path, upload_path);
}


int create_conection(string host_srver, int port){

    int client_socket = 0;
    struct sockaddr_in server_address;
    struct hostent *host;
    std::string copy_url = host_srver;
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

