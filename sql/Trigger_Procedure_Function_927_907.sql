-- =====================================================
-- PET ADOPTION MANAGEMENT SYSTEM (ENHANCED, FIXED)
-- By: Shakirth Anisha, Samridhi Shreya
-- SQL: Triggers, Procedures, and Functions
-- =====================================================

USE pet_adoption_db;

-- ================== TABLES ==================

CREATE TABLE IF NOT EXISTS PetStatusLog (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    pet_id INT,
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pet_id) REFERENCES Pet(pet_id) ON DELETE CASCADE
);

-- ================== STORED PROCEDURES ==================
DELIMITER //

-- Add a new Adoption Application
CREATE PROCEDURE AddAdoptionApplication (
    IN p_user_id INT,
    IN p_pet_id INT,
    IN p_reason TEXT
)
BEGIN
    DECLARE v_status VARCHAR(50);
    SELECT p.status INTO v_status
    FROM pet_adoption_db.Pet p
    WHERE p.pet_id = p_pet_id
    LIMIT 1;

    IF v_status = 'Adopted' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot apply: pet already adopted.';
    END IF;

    INSERT INTO pet_adoption_db.AdoptionApplication (status, reason, approved_by, pet_id, user_id)
    VALUES ('Pending', p_reason, NULL, p_pet_id, p_user_id);
END;
//

-- Reject Adoption Application
CREATE PROCEDURE RejectApplication (
    IN p_app_id INT,
    IN p_reason TEXT
)
BEGIN
    UPDATE pet_adoption_db.AdoptionApplication
    SET status = 'Denied',
        reason = p_reason
    WHERE adopt_app_id = p_app_id;

    UPDATE pet_adoption_db.Payment
    SET status = 'Refunded'
    WHERE adoption_app_id = p_app_id AND status <> 'Refunded';
END;
//

-- Auto Reject Other Applications (exclude the approved one)
CREATE PROCEDURE AutoRejectOtherApplications (
    IN p_pet_id INT,
    IN p_exclude_app_id INT
)
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE v_app_id INT;

    DECLARE app_cursor CURSOR FOR
        SELECT adopt_app_id
        FROM pet_adoption_db.AdoptionApplication
        WHERE pet_id = p_pet_id
          AND status = 'Pending'
          AND adopt_app_id <> p_exclude_app_id;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN app_cursor;
    app_loop: LOOP
        FETCH app_cursor INTO v_app_id;
        IF done THEN
            LEAVE app_loop;
        END IF;
        CALL pet_adoption_db.RejectApplication(
            v_app_id,
            'Automatically rejected since the pet has been adopted.'
        );
    END LOOP;
    CLOSE app_cursor;
END;
//

-- Approve Adoption Application
CREATE PROCEDURE ApproveApplication (
    IN p_app_id INT,
    IN p_worker_id INT
)
BEGIN
    DECLARE v_pet_id INT;
    DECLARE v_pet_status VARCHAR(50);

    SELECT a.pet_id INTO v_pet_id
    FROM pet_adoption_db.AdoptionApplication a
    WHERE a.adopt_app_id = p_app_id
    LIMIT 1;

    IF v_pet_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Adoption application not found.';
    END IF;

    SELECT p.status INTO v_pet_status
    FROM pet_adoption_db.Pet p
    WHERE p.pet_id = v_pet_id
    LIMIT 1;

    IF v_pet_status = 'Adopted' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'This pet has already been adopted.';
    END IF;

    UPDATE pet_adoption_db.AdoptionApplication a
    SET a.status = 'Approved',
        a.approved_by = p_worker_id
    WHERE a.adopt_app_id = p_app_id;

    UPDATE pet_adoption_db.Payment pay
    SET pay.status = 'Completed'
    WHERE pay.adoption_app_id = p_app_id AND pay.status <> 'Completed';

    UPDATE pet_adoption_db.Pet
    SET status = 'Adopted'
    WHERE pet_id = v_pet_id;

    CALL pet_adoption_db.AutoRejectOtherApplications(v_pet_id, p_app_id);
END;
//

-- Register a New Pet
CREATE PROCEDURE RegisterPet (
    IN p_name VARCHAR(100),
    IN p_gender ENUM('M','F','Unknown'),
    IN p_age INT,
    IN p_reason TEXT,
    IN p_status ENUM('Available','Adopted','Medical Hold','Reserved'),
    IN p_shelter_id INT,
    IN p_type_id INT
)
BEGIN
    INSERT INTO pet_adoption_db.Pet (name, gender, age, reason, status, shelter_id, type_id)
    VALUES (p_name, p_gender, p_age, p_reason, p_status, p_shelter_id, p_type_id);
END;
//

-- Update Payment Status
CREATE PROCEDURE UpdatePaymentStatus (
    IN p_pay_id INT,
    IN p_status ENUM('Completed','Pending','Failed','Refunded')
)
BEGIN
    UPDATE pet_adoption_db.Payment
    SET status = p_status
    WHERE pay_id = p_pay_id;
END;
//

-- PROCEDURE: GetAdoptedPetsByUsers
CREATE PROCEDURE GetAdoptedPetsByUsers ()
BEGIN
    SELECT 
        u.user_id AS UserID,
        u.name AS UserName,
        p.pet_id AS PetID,
        p.name AS PetName
    FROM pet_adoption_db.AdoptionApplication a
    JOIN pet_adoption_db.User u ON a.user_id = u.user_id
    JOIN pet_adoption_db.Pet p ON a.pet_id = p.pet_id
    WHERE a.status = 'Approved';
END;
//
DELIMITER ;

-- ====================== TRIGGERS ======================

DELIMITER //

-- Trigger: When application is approved, update pet and payment (no recursion)
CREATE TRIGGER trg_update_pet_status_on_approval
AFTER UPDATE ON pet_adoption_db.AdoptionApplication
FOR EACH ROW
BEGIN
    IF NEW.status = 'Approved' AND OLD.status <> 'Approved' THEN
        UPDATE pet_adoption_db.Pet
        SET status = 'Adopted'
        WHERE pet_id = NEW.pet_id;

        UPDATE pet_adoption_db.Payment
        SET status = 'Completed'
        WHERE adoption_app_id = NEW.adopt_app_id AND status <> 'Completed';
    END IF;
END;
//

-- Trigger: Log Pet status changes
CREATE TRIGGER trg_log_pet_status_change
BEFORE UPDATE ON pet_adoption_db.Pet
FOR EACH ROW
BEGIN
    IF OLD.status <> NEW.status THEN
        INSERT INTO pet_adoption_db.PetStatusLog (pet_id, old_status, new_status)
        VALUES (OLD.pet_id, OLD.status, NEW.status);
    END IF;
END;
//

-- Trigger: Prevent adoption for already adopted pet
CREATE TRIGGER trg_prevent_duplicate_adoption
BEFORE INSERT ON pet_adoption_db.AdoptionApplication
FOR EACH ROW
BEGIN
    DECLARE pet_stat VARCHAR(50);
    SELECT p.status INTO pet_stat
    FROM pet_adoption_db.Pet p
    WHERE p.pet_id = NEW.pet_id
    LIMIT 1;

    IF pet_stat = 'Adopted' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'This pet has already been adopted.';
    END IF;
END;
//
DELIMITER ;

-- ================== FUNCTIONS ==================
DELIMITER //

CREATE FUNCTION CountAvailablePets (p_shelter_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE pet_count INT;
    SELECT COUNT(*) INTO pet_count
    FROM pet_adoption_db.Pet
    WHERE shelter_id = p_shelter_id AND status = 'Available';
    RETURN pet_count;
END;
//

CREATE FUNCTION TotalAdoptionsByUser (p_user_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE total_adopted INT;
    SELECT COUNT(*) INTO total_adopted
    FROM pet_adoption_db.AdoptionApplication
    WHERE user_id = p_user_id AND status = 'Approved';
    RETURN total_adopted;
END;
//

CREATE FUNCTION AvgPetAgeInShelter (p_shelter_id INT)
RETURNS DECIMAL(5,2)
DETERMINISTIC
BEGIN
    DECLARE avg_age DECIMAL(5,2);
    SELECT AVG(age) INTO avg_age
    FROM pet_adoption_db.Pet
    WHERE shelter_id = p_shelter_id;
    RETURN avg_age;
END;
//
DELIMITER ;

-- ===================== TEST / EXAMPLE USAGE ========================

-- RegisterPet Procedure
SELECT * FROM Pet;
CALL RegisterPet('Buddy', 'M', 3, 'Friendly and playful', 'Available', 1, 1);
SELECT * FROM Pet;

-- AddAdoptionApplication Procedure
SELECT * FROM AdoptionApplication;
CALL AddAdoptionApplication(9, 7, 'Looking to adopt a friendly dog');
SELECT * FROM AdoptionApplication;

-- Approve a pending application and auto trigger adoption + reject others
SELECT * FROM Pet WHERE pet_id = 5;  -- Zoomie
SELECT * FROM AdoptionApplication WHERE pet_id = 5;
SELECT * FROM Payment WHERE adoption_app_id IN (SELECT adopt_app_id FROM AdoptionApplication WHERE pet_id = 5);

CALL ApproveApplication(1, 2);

SELECT * FROM Pet WHERE pet_id = 5;
SELECT * FROM AdoptionApplication WHERE pet_id = 5;
SELECT * FROM Payment WHERE adoption_app_id IN (SELECT adopt_app_id FROM AdoptionApplication WHERE pet_id = 5);
SELECT * FROM PetStatusLog WHERE pet_id = 5;


-- AutoRejectOtherApplications Trigger
INSERT INTO AdoptionApplication (status, reason, pet_id, user_id) VALUES ('Pending', 'Love small cats', 3, 7);
INSERT INTO AdoptionApplication (status, reason, pet_id, user_id) VALUES ('Pending', 'Perfect for family', 3, 9);

SELECT * FROM AdoptionApplication WHERE pet_id = 3;
SELECT * FROM Pet WHERE pet_id = 3;

CALL ApproveApplication(4, 5);

SELECT * FROM AdoptionApplication WHERE pet_id = 3;
SELECT * FROM Pet WHERE pet_id = 3;
SELECT * FROM PetStatusLog WHERE pet_id = 3;


-- RejectApplication Procedure
SELECT * FROM AdoptionApplication WHERE adopt_app_id = 3;
SELECT * FROM Payment WHERE adoption_app_id = 3;

CALL RejectApplication(3, 'User withdrew application');

SELECT * FROM AdoptionApplication WHERE adopt_app_id = 3;
SELECT * FROM Payment WHERE adoption_app_id = 3;


-- UpdatePaymentStatus Procedure
SELECT * FROM Payment WHERE pay_id = 2;

CALL UpdatePaymentStatus(2, 'Completed');

SELECT * FROM Payment WHERE pay_id = 2;


-- Pet Status Log Trigger
SELECT * FROM PetStatusLog;
UPDATE Pet SET status = 'Medical Hold' WHERE pet_id = 6;
SELECT * FROM PetStatusLog;

-- GetAdoptedPetsByUsers Procedure
CALL GetAdoptedPetsByUsers();

-- TESTING FUNCTIONS
-- CountAvailablePets
SELECT CountAvailablePets(1) AS AvailablePets_In_Shelter1;

-- TotalAdoptionsByUser
SELECT TotalAdoptionsByUser(3) AS Total_Adoptions_By_Angad;

-- AvgPetAgeInShelter
SELECT AvgPetAgeInShelter(1) AS Avg_Age_Shelter1;

-- ====================== DONE ===============================