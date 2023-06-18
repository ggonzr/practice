// Task data structure
use chrono::{serde::ts_seconds, DateTime, Local, Utc};
use serde::Deserialize;
use serde::Serialize;

// File I/O operations
use std::fs::{File, OpenOptions};
use std::path::PathBuf;
// Not nice that it is required to control the buffer stream
// for reading a file by default
use std::fmt;
use std::io::{Error, ErrorKind, Result, Seek, SeekFrom};

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
    pub created_at: DateTime<Utc>,
}

// Methods
impl Task {
    pub fn new(text: String) -> Task {
        let created_at: DateTime<Utc> = Utc::now();
        // Remember the implicit return
        Task { text, created_at }
    }
}

// Implement Display trait
impl fmt::Display for Task {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let created_at = self.created_at.with_timezone(&Local).format("%F %H:%M");
        write!(f, "{:<50} [{}]", self.text, created_at)
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
    Ok(())
}

// Read the task file and read its content
fn collect_tasks(mut file: &File) -> Result<Vec<Task>> {
    file.seek(SeekFrom::Start(0))?; // Rewind the file before.
    let tasks = match serde_json::from_reader(file) {
        Ok(tasks) => tasks,
        Err(e) if e.is_eof() => Vec::new(),
        Err(e) => Err(e)?,
    };
    file.seek(SeekFrom::Start(0))?; // Rewind the file after.
    Ok(tasks)
}

// Read the list of tasks and delete one, beware of File pointer when deleting
// something
pub fn complete_task(journal_path: PathBuf, task_position: usize) -> Result<()> {
    // Open the file.
    let file = OpenOptions::new()
        .read(true)
        .write(true)
        .open(journal_path)?;

    // Consume file's contents as a vector of tasks.
    let mut tasks = collect_tasks(&file)?;

    // Try to remove the task.
    if task_position == 0 || task_position > tasks.len() {
        // ErrorKind seems to be an enum with several
        // options for specific custom errors
        return Err(Error::new(ErrorKind::InvalidInput, "Invalid Task ID"));
    }

    // Remove the element
    tasks.remove(task_position - 1);

    // Write the modified task list back into the file.
    // Use a blank page, truncate the file
    file.set_len(0)?;
    serde_json::to_writer(file, &tasks)?;
    Ok(())
}

// Display all Tasks available into the file
pub fn list_tasks(journal_path: PathBuf) -> Result<()> {
    // Open file
    let file = OpenOptions::new().read(true).open(journal_path)?;
    let tasks = collect_tasks(&file)?;
    if tasks.is_empty() {
        println!("Task list is empty")
    } else {
        let mut order: u32 = 1;
        for task in tasks {
            println!("{}: {}", order, task);
            order += 1;
        }
    }
    Ok(())
}
