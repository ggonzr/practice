// Task data structure
use chrono::{serde::ts_seconds, DateTime, Local, Utc};
use serde::Deserialize;
use serde::Serialize;

// File I/O operations
use std::fs::{File, OpenOptions};
use std::path::PathBuf;
// Not nice that it is required to control the buffer stream
// for reading a file by default
use std::io::{Result, Seek, SeekFrom};

// Struct fields
// We can include several attributes using derive
// to allow our structure to include some trait implementations
// This traits implement serialization features
#[derive(Debug, Deserialize, Serialize)]
pub struct Task {
    pub text: String,
    // Anotate the following field
    // This indicates how serde can serialize this field
    #[serde(with = "ts_seconds")]
    pub created_at: DateTime<Local>,
}

// Methods
impl Task {
    pub fn new(text: String) -> Task {
        let created_at: DateTime<Local> = Local::now();
        // Remember the implicit return
        Task { text };
    }
}

// Functions for I/O operations
// Result<()> represents a result type for an I/O operation
// Ok semantics here means that the I/O operation finished successfully

pub fn add_task(journal_path: PathBuf, task: Task) -> Result<()> {
    // Open the file
    let mut file = OpenOptions::new()
        // File permissions
        .read(true)
        .write(true)
        .create(true)
        // ? := ErrorPropagationExpression
        // This operator performs the unwrap operation
        // or inmediatly returns an error if this happens
        // or None if we are working with Option<T>
        .open(journal_path)?;

    // Consume the file content and store it as a
    // vector of tasks
    let mut tasks: Vec<Task> = match serde_json::from_reader(&file) {
        Ok(tasks) => tasks,
        // Return an empty vector if the file is empty
        Err(e) if e.is_eof() => Vec::new(),
        // Raise another kind of error
        Err(e) => Err(e)?,
    };

    // Set the buffer pointer at the beginning
    // Rewind the file after reading from it.
    file.seek(SeekFrom::Start(0))?;

    // Write the content into the file
    // Include the new task
    tasks.push(task);
    // Persist the file
    serde_json::to_writer(file, &tasks)?;

    // Return a Ok signal to express the I/O operation finished
    // successfully
    Ok(());
}
