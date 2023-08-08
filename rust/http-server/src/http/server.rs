use chunked_transfer::Encoder;
use std::{
    fmt::Debug,
    fs,
    io::{prelude::*, BufReader},
    net::{TcpListener, TcpStream},
};
type IOError = std::io::Error;
type FormatError = std::fmt::Error;

pub trait HTTPServer {
    fn new(addr: &str) -> Result<Self, IOError>
    where
        Self: Sized;
    fn server(&self) -> &TcpListener;
    fn process(&self);
}
pub struct SimpleHTTPServer {
    addr: String,
    server: TcpListener,
}

impl SimpleHTTPServer {
    fn parse_http_headers(connection: &TcpStream) -> Vec<String> {
        let buf_reader = BufReader::new(connection);
        buf_reader
            .lines()
            .map(|l| l.unwrap())
            .take_while(|l| !l.is_empty())
            .collect()
    }

    fn send_success_response(&self, mut stream: TcpStream) {
        // Send an HTTP 200 response
        // Remember: \r\n means CRLF (carriage return, line feed),
        // If you append two of them, it means the HTTP response has finished
        let content = vec![
            "HTTP/2 200 Party time",
            "Content-Type: application/json; charset=UTF-8",
            "",
            "{\"message\": \"It's friday, have a nice day :) !\"}",
            "\r\n",
        ];
        let content = content.join("\r\n");
        stream.write_all(content.as_bytes()).unwrap();
    }

    fn send_error_response(&self, mut stream: TcpStream, file: &str) {
        let file = fs::read(file).unwrap();
        let file_size = file.len();

        // Encode the file as chunks
        let mut encoded = Vec::new();
        {
            let mut encoder = Encoder::with_chunks_size(&mut encoded, 8);
            encoder.write_all(&file).unwrap();
        }

        let content_lenght = &format!("Content-Lenght: {}", file_size)[..];
        let content = [
            "HTTP/2 400 C'mon at least read the docs .____. Wait, are there docs?",
            "Content-Type: image/jpg",
            content_lenght,
            "Transfer-Encoding: chunked",
            "\r\n",
        ];
        let mut content = content.join("\r\n").to_string().into_bytes();
        content.extend(&encoded);
        stream.write_all(&content).unwrap();
    }
}

impl HTTPServer for SimpleHTTPServer {
    fn new(addr: &str) -> Result<Self, IOError> {
        let server = TcpListener::bind(addr);
        let addr = addr.to_string();

        // A not simple cast just to bind something as its interface
        // let wrapper = Box::new(send_success_response) as Box<dyn FnMut(TcpStream)>;
        // In the example above, it is not possible to access the function available into the
        // heap via function pointers to execute it. We can not perform the move to call the function

        match server {
            Ok(server) => Ok(SimpleHTTPServer { addr, server }),
            Err(e) => Err(e),
        }
    }
    fn server(&self) -> &TcpListener {
        &self.server
    }
    fn process(&self) {
        for connection in self.server().incoming() {
            let connection = connection.unwrap();
            let headers = SimpleHTTPServer::parse_http_headers(&connection);
            let resource: &str = &headers[0];
            let root_resource = "GET / HTTP/1.1";
            match resource {
                _ if resource == root_resource => self.send_success_response(connection),
                _ => self.send_error_response(connection, "public/disappointed.jpg"),
            }
        }
    }
}

impl Debug for SimpleHTTPServer {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> Result<(), FormatError> {
        write!(f, "SimpleHTTPServer {{ addr: {} }}", self.addr)
    }
}
