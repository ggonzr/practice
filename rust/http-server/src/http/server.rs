use super::response::{send_error_response, send_success_response};
use std::{
    fmt::Debug,
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
                _ if resource == root_resource => send_success_response(connection),
                _ => send_error_response(connection, "public/disappointed.jpg"),
            }
        }
    }
}

impl Debug for SimpleHTTPServer {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> Result<(), FormatError> {
        write!(f, "SimpleHTTPServer {{ addr: {} }}", self.addr)
    }
}
