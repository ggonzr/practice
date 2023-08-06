mod http;
use http::response::handle_connection;
use http::server::{HTTPServer, SimpleHTTPServer};

fn main() {
    let addr: &str = "127.0.0.1:8000";
    let server = SimpleHTTPServer::new(addr);
    if let Ok(listener) = server {
        println!("Server listening on port 8000");
        for stream in listener.server().incoming() {
            if let Ok(s) = stream {
                handle_connection(s);
            }
        }
    } else {
        println!("Server failed to bind to port 8000");
    }
}
