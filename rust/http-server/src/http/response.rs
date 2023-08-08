/// This module handles how to respond to a HTTP request.
use chunked_transfer::Encoder;
use std::{
    fs,
    io::{prelude::*, BufReader},
    net::TcpStream,
};

fn parse_http_headers(connection: &TcpStream) -> Vec<String> {
    let buf_reader = BufReader::new(connection);
    buf_reader
        .lines()
        .map(|l| l.unwrap())
        .take_while(|l| !l.is_empty())
        .collect()
}

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

pub fn handle_connection(connection: TcpStream) {
    let headers = self::parse_http_headers(&connection);
    let resource: &str = &headers[0];
    let root_resource = "GET / HTTP/1.1";
    match resource {
        _ if resource == root_resource => self::send_success_response(connection),
        _ => self::send_error_response(connection, "public/disappointed.jpg"),
    }
}
