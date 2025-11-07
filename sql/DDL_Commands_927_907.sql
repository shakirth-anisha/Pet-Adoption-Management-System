-- =====================================================
-- Pet Adoption Management System
-- By: Shakirth Anisha, Samridhi Shreya
-- SQL: DDL, DML Commands
-- =====================================================

DROP DATABASE IF EXISTS pet_adoption_db;
CREATE DATABASE IF NOT EXISTS pet_adoption_db;
USE pet_adoption_db;

-- ================== CREATING TABLES ==================

CREATE TABLE User (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(20),
    role ENUM('general', 'adopter', 'shelter_worker', 'admin') DEFAULT 'general',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE Shelter (
    shelter_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(255) NOT NULL,
    contact VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE ShelterWorker (
    worker_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    shelter_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
    FOREIGN KEY (shelter_id) REFERENCES Shelter(shelter_id) ON DELETE CASCADE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE PetType (
    type_id INT AUTO_INCREMENT PRIMARY KEY,
    species VARCHAR(50) NOT NULL,
    breed VARCHAR(50),
    life_span INT CHECK (life_span >= 0),
    size ENUM('Small', 'Medium', 'Large', 'Giant'),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Pet (
    pet_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    gender ENUM('M', 'F', 'Unknown') DEFAULT 'Unknown',
    age INT CHECK (age >= 0),
    reason TEXT,
    status ENUM('Available', 'Adopted', 'Medical Hold') DEFAULT 'Available',
    shelter_id INT NOT NULL,
    type_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (shelter_id) REFERENCES Shelter(shelter_id) ON DELETE CASCADE,
    FOREIGN KEY (type_id) REFERENCES PetType(type_id),
    CONSTRAINT unique_pet_per_shelter UNIQUE (name, shelter_id),
    CONSTRAINT chk_pet_status CHECK (status IN ('Available', 'Adopted', 'Medical Hold'))
);

CREATE TABLE PetImages (
    image_id INT AUTO_INCREMENT PRIMARY KEY,
    pet_id INT NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    FOREIGN KEY (pet_id) REFERENCES Pet(pet_id) ON DELETE CASCADE
);

CREATE TABLE AdoptionApplication (
    adopt_app_id INT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Pending', 'Approved', 'Denied', 'Withdrawn') DEFAULT 'Pending',
    reason TEXT,
    approved_by INT,
    pet_id INT NOT NULL,
    user_id INT NOT NULL,
    FOREIGN KEY (approved_by) REFERENCES ShelterWorker(worker_id),
    FOREIGN KEY (pet_id) REFERENCES Pet(pet_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Payment (
    pay_id INT AUTO_INCREMENT PRIMARY KEY,
    method ENUM('Credit Card', 'Debit Card', 'UPI', 'PayPal', 'Cash') NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
    status ENUM('Completed', 'Pending', 'Failed', 'Refunded') DEFAULT 'Pending',
    user_id INT NOT NULL,
    adoption_app_id INT,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (adoption_app_id) REFERENCES AdoptionApplication(adopt_app_id) ON DELETE CASCADE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_amount_positive CHECK (amount >= 0)
);

CREATE TABLE Review (
    rev_id INT AUTO_INCREMENT PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    reviewer_id INT NOT NULL,
    shelter_id INT,
    pet_id INT,
    FOREIGN KEY (reviewer_id) REFERENCES User(user_id) ON DELETE CASCADE,
    FOREIGN KEY (shelter_id) REFERENCES Shelter(shelter_id) ON DELETE CASCADE,
    FOREIGN KEY (pet_id) REFERENCES Pet(pet_id) ON DELETE SET NULL
);

-- ================== VIEWS ==================
CREATE VIEW AvailablePets AS
SELECT 
    p.pet_id, p.name, pt.species, pt.breed, 
    s.name AS shelter_name, p.status
FROM Pet p
JOIN PetType pt ON p.type_id = pt.type_id
JOIN Shelter s ON p.shelter_id = s.shelter_id
WHERE p.status = 'Available';

CREATE VIEW AdoptionSummary AS
SELECT 
    a.adopt_app_id,
    u.name AS adopter_name,
    p.name AS pet_name,
    a.status AS application_status,
    s.name AS shelter_name,
    a.date
FROM AdoptionApplication a
JOIN User u ON a.user_id = u.user_id
JOIN Pet p ON a.pet_id = p.pet_id
JOIN Shelter s ON p.shelter_id = s.shelter_id;

-- ================== INSERT DATA ==================

INSERT INTO User (name, email, phone, role) VALUES
('Shakirth Anisha', 'anisha@petsystem.com', '9876543210', 'admin'),
('Samridhi Shreya', 'samridhi@petsystem.com', '9876501234', 'shelter_worker'),
('Angad Bhalla', 'angad@petsystem.com', '9876003210', 'adopter'),
('Suchitra Shankar', 'suchitra@petsystem.com', '9876123456', 'adopter'),
('Tejas R', 'tejas@petsystem.com', '9988776655', 'shelter_worker'),
('Sanjana Saxena', 'sanjana@petsystem.com', '9123456789', 'general'),
('Risu Kumari', 'risu@petsystem.com', '9765432109', 'adopter'),
('Taylor Swift', 'taylor@petsystem.com', '9000011122', 'adopter'),
('Harry Styles', 'harry@petsystem.com', '7086011282', 'adopter'),
('Emma Stone', 'emma@petsystem.com', '7086921122', 'shelter_worker'),
('John Wick', 'john@petsystem.com', '8012346772', 'shelter_worker');

-- SHELTERS
INSERT INTO Shelter (name, location, contact)
VALUES
('PES EC Campus, Bangalore', 'Electronic City, Bangalore', 'pesec@petshelter.org'),
('Paws Shelter', 'Electronic City, Bangalore', 'paws@petshelter.org'),
('Happy Tails Home', 'Chennai, India', 'contact@happytails.in'),
('Pawfect Care Foundation', 'Bangalore', 'contact@pawfectcare.in'),
('Animal Ark Trust', 'Hyderabad', 'support@animalarktrust.org'),
('StreetPaws Rehabilitation', 'Delhi', 'help@streetpaws.org');

-- SHELTER WORKERS
INSERT INTO ShelterWorker (user_id, shelter_id)
VALUES
(1, 5),   -- Anisha at Animal Ark Trust
(2, 2),  -- Samridhi at Paws Shelter
(5, 1),  -- Tejas at PES EC Campus
(10, 3),  -- Emma at Happy Tails Home
(11, 4);   -- John at Pawfect Care Foundation

-- PET TYPES
INSERT INTO PetType (species, breed, life_span, size)
VALUES
('Dog', 'Shih Tzu', 12, 'Small'),
('Dog', 'Beagle', 14, 'Medium'),
('Cat', 'Persian', 15, 'Small'),
('Parrot', 'African Grey', 50, 'Small'),
('Rabbit', 'Holland Lop', 10, 'Small'),
('Dog', 'German Shepherd', 10, 'Large'),
('Cat', 'Calico', 14, 'Small');

-- PETS
INSERT INTO Pet (name, gender, age, reason, status, shelter_id, type_id)
VALUES
('Yuki', 'M', 3, 'Owner relocation', 'Adopted', 1, 1),
('Milo', 'M', 2, 'Found stray', 'Adopted', 2, 6),
('Luna', 'F', 1, 'Abandoned kitten', 'Available', 1, 7),
('Snowball', 'F', 4, 'Health issues', 'Medical Hold', 3, 5),
('Zoomie', 'F', 2, 'Rescued stray cat', 'Available', 2, 3),
('Coco', 'M', 1, 'Owner could not care for it', 'Available', 3, 4),
('Coffee', 'F', 2, 'Rescued stray cat', 'Adopted', 2, 7);

-- PET IMAGES
INSERT INTO PetImages (pet_id, image_url)
VALUES
(1, "https://i.anga.codes/i/5zaft9djp9rh/ShihTzu.png"),
(1, ""),
(1, ""),
(1, ""),
(1, ""),
(1, ""),
(1, "");

-- ADOPTION APPLICATIONS
INSERT INTO AdoptionApplication (status, reason, approved_by, pet_id, user_id)
VALUES
('Pending', 'Want to adopt a cat for my family', NULL, 5, 4), -- Suchitra applying for Zoomie
('Approved', 'Looking for a friendly dog', 1, 1, 3), -- Angad approved for Yuki
('Pending', 'Not enough space at home', NULL, 2, 7), -- Risu denied for Milo
('Pending', 'Want a small pet for my apartment', NULL, 3, 8), -- Taylor applying for Luna
('Approved', 'Need a companinion', 2, 2, 9), -- Harry applying for Milo
('Approved', 'Looking for a companion for my dog', 1, 7, 3); -- Angad approved for Coffee

-- PAYMENTS

INSERT INTO Payment (method, amount, status, user_id, adoption_app_id)
VALUES
('Credit Card', 1500.00, 'Completed', 3, 2),   -- Angad pays for adopting Yuki
('UPI', 200.00, 'Pending', 4, 1),             -- Suchitra’s payment is pending for Zoomie
('PayPal', 800.00, 'Completed', 8, 3),         -- Taylor’s payment completed for Coco
('Debit Card', 950.00, 'Failed', 9, 5),         -- Taylor’s payment completed for Coco
('Credit Card', 950.00, 'Completed', 9, 5);         -- Taylor’s payment completed for Coco


-- ==========================================

UPDATE Pet
SET gender = 'M'
WHERE name = 'Zoomie';

DELETE FROM PetType WHERE type_id = 2;
DELETE FROM Payment WHERE status = 'Failed';

SELECT
    p.pet_id,
    p.name AS Pet_Name,
    pt.species AS Species,
    pt.breed AS Breed,
    p.age AS Age,
    p.gender AS Gender,
    p.status AS Status,
    s.name AS Shelter_Name
FROM Pet p
JOIN PetType pt ON p.type_id = pt.type_id
JOIN Shelter s ON p.shelter_id = s.shelter_id
ORDER BY pt.species, p.name;

SELECT
    u.user_id,
    u.name AS User_Name,
    u.email AS Email,
    p.method AS Payment_Method,
    p.amount AS Amount,
    p.status AS Payment_Status,
    p.date AS Payment_Date
FROM Payment p
JOIN User u ON p.user_id = u.user_id
ORDER BY p.date DESC;

-- ================== DONE ==================
