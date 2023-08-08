mod http;
use http::server::{HTTPServer, SimpleHTTPServer};

pub fn run() {
    let addr: &str = "127.0.0.1:8000";
    let server = SimpleHTTPServer::new(addr);
    if let Ok(listener) = server {
        println!("Server listening on port 8000");
        listener.run();
    } else {
        println!("Server failed to bind to port 8000");
    }
}
