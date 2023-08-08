/// This implements a ThreadPoolExecutor for the HTTP server.
use std::{
    fmt::Debug,
    sync::{mpsc, Arc, Mutex},
    thread,
};
type Job = Box<dyn FnOnce() + Send + 'static>;

pub struct ThreadPool {
    /// The number of threads in the pool.
    workers: Vec<Worker>,
    sender: mpsc::Sender<Job>,
}
impl ThreadPool {
    /// Create a new ThreadPoolExecutor.
    ///
    /// The size is the number of threads in the pool.
    ///
    /// # Panics
    ///
    /// The `new` function will panic if the size is zero.
    pub fn new(size: usize) -> ThreadPool {
        assert!(size > 0);

        let (sender, receiver) = mpsc::channel();
        let receiver = Arc::new(Mutex::new(receiver));
        let mut workers = Vec::with_capacity(size);

        for id in 0..size {
            workers.push(Worker::new(id, Arc::clone(&receiver)));
        }

        ThreadPool { workers, sender }
    }

    pub fn execute<F>(&self, f: F)
    where
        F: FnOnce() + Send + 'static,
    {
        let job = Box::new(f);
        self.sender.send(job).unwrap();
    }
}

struct Worker {
    id: usize,
    thread: thread::JoinHandle<()>,
}

impl Worker {
    fn new(id: usize, receiver: Arc<Mutex<mpsc::Receiver<Job>>>) -> Worker {
        let thread = thread::spawn(move || loop {
            let job = receiver
                .lock()
                .expect("Unable to lock, maybe some thread has panicked")
                .recv()
                .unwrap();
            println!("Worker {id} got a job; executing.");
            // Execute the function send by ThreadPool
            job();
        });

        Worker { id, thread }
    }
}

impl Debug for Worker {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> Result<(), std::fmt::Error> {
        write!(f, "{{ id: {} }}", self.id)
    }
}
