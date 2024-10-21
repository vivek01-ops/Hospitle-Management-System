import sqlite3  # or your specific database connector

def connect_db():
    conn = sqlite3.connect('hospitle_database.db')  # Use your database name here
    cursor = conn.cursor()
    
    # Create doctors table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            contact TEXT NOT NULL,
            availability TEXT NOT NULL
        );
    ''')
    
    # Create patients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dob DATE NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            contact TEXT NOT NULL,
            date_of_admission DATE NOT NULL,
            address TEXT NOT NULL,
            medical_history TEXT,
            allergies TEXT,
            chronic TEXT,
            surgery TEXT,
            medications TEXT
        );
    ''')

    # Create billing table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS billing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            amount REAL,
            status TEXT,
            date DATE,
            FOREIGN KEY (patient_id) REFERENCES patients (id)
        );
    ''')
    
    # Create appointment table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            doctor_name TEXT,
            date_time DATETIME,
            reason TEXT,
            FOREIGN KEY (name) REFERENCES patients(id),
            FOREIGN KEY (doctor_name) REFERENCES doctors(id)
    );
    ''')

    conn.commit()
    return conn
