use chunked_transfer::Encoder;
use std::{
    fs,
    io::{prelude::*, BufReader},
    net::{TcpListener, TcpStream},
};

fn send_success_response(mut stream: TcpStream) {
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

fn send_error_response(mut stream: TcpStream, file: &str) {
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

fn handle_connection(mut stream: TcpStream) {
    // Read the request body as text following the HTTP protocol
    let buf_reader = BufReader::new(&mut stream);
    // Parse request headers
    let http_request: Vec<_> = buf_reader
        .lines()
        .map(|l| l.unwrap())
        .take_while(|l| !l.is_empty())
        .collect();

    // println!("Request: {:?}", http_request);
    let resource: &str = &http_request[0];
    let root_resource = "GET / HTTP/1.1";
    match resource {
        _ if resource == root_resource => send_success_response(stream),
        _ => send_error_response(stream, "public/disappointed.jpg"),
    }
}

fn main() {
    let addr: &str = "127.0.0.1:8000";
    let server_listener = TcpListener::bind(addr);
    if let Ok(listener) = server_listener {
        println!("Server listening on port 8000");
        for stream in listener.incoming() {
            if let Ok(s) = stream {
                handle_connection(s);
            }
        }
    } else {
        println!("Server failed to bind to port 8000");
    }
}
