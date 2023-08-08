use super::{executor::ThreadPool, response::handle_connection};
use std::{fmt::Debug, net::TcpListener};
type IOError = std::io::Error;
type FormatError = std::fmt::Error;

pub trait HTTPServer {
    fn new(addr: &str) -> Result<Self, IOError>
    where
        Self: Sized;
    fn server(&self) -> &TcpListener;
    fn run(&self);
}
pub struct SimpleHTTPServer {
    addr: String,
    server: TcpListener,
    pool: ThreadPool,
}

impl SimpleHTTPServer {}

impl HTTPServer for SimpleHTTPServer {
    fn new(addr: &str) -> Result<Self, IOError> {
        let server = TcpListener::bind(addr);
        let addr = addr.to_string();
        let pool = ThreadPool::new(4);

        // A not simple cast just to bind something as its interface
        // let wrapper = Box::new(send_success_response) as Box<dyn FnMut(TcpStream)>;
        // In the example above, it is not possible to access the function available into the
        // heap via function pointers to execute it. We can not perform the move to call the function

        match server {
            Ok(server) => Ok(SimpleHTTPServer { addr, server, pool }),
            Err(e) => Err(e),
        }
    }
    fn server(&self) -> &TcpListener {
        &self.server
    }

    fn run(&self) {
        for connection in self.server().incoming() {
            self.pool.execute(move || {
                handle_connection(connection.unwrap());
            })
        }
    }
}

impl Debug for SimpleHTTPServer {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> Result<(), FormatError> {
        write!(f, "SimpleHTTPServer {{ addr: {} }}", self.addr)
    }
}
