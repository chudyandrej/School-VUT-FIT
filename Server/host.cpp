//
// Created by Andrej Oliver Chudý on 13/04/16.
//

#include "host.h"

/**
 * Function for procesing reqest of client 
 * 
 * @param request_MSG - Request split by commas
 */
void Client::service_request(std::vector<std::string> request_MSG) {
    if (request_MSG.size() > 0) {                      
        if (request_MSG[0] == "D" && request_MSG.size() == 2) {     //Request to download someting
            upload(communication_socket,request_MSG[1]);             //Program upload it
            
        }
        else if (request_MSG[0] == "U" && request_MSG.size() == 3 ) {           //Request to upload someting 
            download(communication_socket, request_MSG[1], request_MSG[2]);      //Program download it form client 
            
        }
        else {
            sendMessage(communication_socket,"SYN");            //Program didn't understand request
        }
    }
    else{
       sendMessage(communication_socket,"EMP");                 //Request was empty 
    }
}

/**
 * This function downloading file from client (clinet uploading). 
 * 
 * @param socket - Communication socekt 
 * @param filename - Name of downloaded file
 * @param str_fileSIZE -  Size of downloaded file
 * @return Exit status if operation end successfully
 */
void Client::download(int socket, std::string filename, std::string str_fileSIZE) {
    char buffer[BUFFER_SIZE];
    long fileSIZE;
    std::vector<std::string> request_summary;
    std::ofstream file;


    fileSIZE = string_to_number(str_fileSIZE);
    file.open(filename, std::ios::binary);

    if( !file.is_open() ){
        sendMessage(socket, "NF");
        perror("Unable to create a file\n ");
        return ;
    }

   if (sendMessage(socket,"OK") != SUCCS){           //Send message that server is ready to upload
        perror("Problem whit conncetion whit client");
        return;
    }       
   // printf("%s  %s\n",filename.c_str(),str_fileSIZE.c_str() );
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
        perror("Error some data was lost. File is incomplete. This file will be deleted.");
        sendMessage(socket, "INC");  
        remove( filename.c_str() );
        return ;
    }
    sendMessage(socket, "OK");  
}

/**
 * This function upload file to client (clinet donwloading). 
 * 
 * @param socket - Communication socekt 
 * @param filename - Name of file what client want
 * @return Exit status if operation end successfully
 */
void Client::upload(int socket, std::string filename){
    long sizeFILE;
    char buffer[BUFFER_SIZE];
    std::string str_sizeFILE;
    std::ofstream file; 
    
    sizeFILE = fileSizeFunc(filename);      //Chcek size of file and if 
    if (sizeFILE == -1){
        sendMessage(socket,"NF");
        perror("File problem");
        return;
    }
  
    memset(buffer, 0, sizeof(buffer));                  //Delete buffer
    int upload_file = open(filename.c_str(), O_RDONLY);
    int rc = flock(upload_file, LOCK_SH);               //Lock file
    if (rc){
        perror("File lock problem");
        sendMessage(socket,"NF");
        return;
    }

    if (sendMessage(socket,"OK," + number_to_string(sizeFILE)) != SUCCS){           //Send message that server is ready to upload
        perror("Problem whit conncetion whit client");
        return;
    }     

    ssize_t bytes_read = 0;
    ssize_t bytes_written = 0; 
    while (1) {
        memset(buffer, 0, sizeof(buffer));
        bytes_read = read(upload_file, buffer, sizeof(buffer));
        if (bytes_read == 0) { break; }                     //whole file is read
        if (bytes_read < 0) {
            perror("Reading from file FAILED\n");
            return;
        }
        char *buffPtr = buffer;
        while (bytes_read > 0) {
            bytes_written = write(socket, buffPtr, (size_t) bytes_read);
            if (bytes_written <= 0) {
                perror("Sending bytes FAILED");
                return;
            }
            bytes_read -= bytes_written;
            buffPtr += bytes_written;
        }
    }
    file.close();
}


/**
 * Function to chcek size of file 
 * 
 * @param filename - Path of file
 * @return Size of file (byts)
 */
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


/**
 * Function to send message with standard delimiter
 * 
 * @param socket - Communication socekt
 * @param request - Text of message
 * @return Exit status if operation end successfully
 */
int  Client::sendMessage(int socket, std::string message) {
    message = message + "\n\n";
    unsigned long requestLen = message.length() + 1;
    const char *c;

    c = message.c_str();
    int sent = 0;
    int bytes = 0;
    while (sent < (int)requestLen){
        bytes = (int) send(socket, c+sent, (size_t) requestLen, 0);
        if (bytes < 0) {
            perror("Sending message FAILED");
            return FAIL;
        }
        if (bytes == 0) {
            break;
        }
        sent += bytes;
    }
    if(sent != (int)requestLen){
        perror("ERROR: NOT entire message sent");
        return FAIL;
    }
    return SUCCS;
}


/**
 * Function to load request from client
 * 
 * @param socket - Communication socekt
 * @return Vector of message split over protocol delimiter
 */
std::vector<std::string> Client::load_request(int socket){

    char buffer[BUFFER_SIZE];
    memset(buffer, 0, BUFFER_SIZE);
    std::string message;
    int received = 0;
   
    while(true){
        received = recv(socket, buffer, (size_t)(BUFFER_SIZE), 0);
        message = message + std::string(buffer);
        if (received <= 0) {
            break;
        }

        if(message.find("\n\n") != std::string::npos){
            message = replace_string(message,"\n\n","");
            break;
        }
    }
    return split(message,',');
}


/**
 * Function to split input string by some char
 * 
 * @param input - Input string
 * @param delimiter - Char (delimiter)
 * @return Vector of strings
 */
std::vector<std::string> Client::split(std::string input, char delimiter) {
    std::stringstream stream_massage(input);
    std::string segment;
    std::vector<std::string> seglist;

    while(std::getline(stream_massage, segment, delimiter)) {
        seglist.push_back(segment);
    }
    return seglist;
}

/**
 * Function to replace string 
 * 
 * @param input - Input string
 * @param wanted - What you want replace
 * @param for_what - For what you want replace it
 * @return Edit string
 */
std::string Client::replace_string(std::string input, std::string wanted, std::string for_what){
    size_t f = input.find(wanted);
    input.replace(f, std::string(wanted).length(), for_what);
    return input;
}

/**
 * Function to convert string to number (long)
 * 
 * @param input - Input string
 * @return Long number
 */
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


/**
 * Function to convert number to string 
 * 
 * @param input - Input number (long)
 * @return Input number as string
 */
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
