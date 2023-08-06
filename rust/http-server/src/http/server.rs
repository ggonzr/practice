use std::collections::HashMap;
use std::fmt::Debug;
use std::net::{TcpListener, TcpStream};
type IOError = std::io::Error;
type FormatError = std::fmt::Error;
type RouteHandler = Box<dyn FnMut(TcpStream) -> ()>;

pub trait HTTPServer {
    fn new(addr: &str) -> Result<Self, IOError>
    where
        Self: Sized;

    fn route(&mut self, path: &str, handler: RouteHandler);
    fn server(&self) -> &TcpListener;
}
pub struct SimpleHTTPServer {
    addr: String,
    server: TcpListener,
    routes: HashMap<String, RouteHandler>,
}

impl HTTPServer for SimpleHTTPServer {
    fn new(addr: &str) -> Result<Self, IOError> {
        let server = TcpListener::bind(addr);
        let addr = addr.to_string();
        let routes = HashMap::new();
        match server {
            Ok(server) => Ok(SimpleHTTPServer {
                addr,
                server,
                routes,
            }),
            Err(e) => Err(e),
        }
    }
    fn route(&mut self, path: &str, handler: RouteHandler) {
        self.routes.insert(path.to_string(), handler);
    }
    fn server(&self) -> &TcpListener {
        &self.server
    }
}

impl Debug for SimpleHTTPServer {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> Result<(), FormatError> {
        write!(f, "SimpleHTTPServer {{ addr: {} }}", self.addr)
    }
}
