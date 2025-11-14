-- =====================================================
-- Pet Adoption Management System
-- By: Shakirth Anisha, Samridhi Shreya
-- SQL: DDL, DML Commands
-- =====================================================

USE pet_adoption_db;

-- ================== CLEAN UP EXISTING ROLES ==================
DROP ROLE IF EXISTS 'admin_role';
DROP ROLE IF EXISTS 'shelter_worker_role';
DROP ROLE IF EXISTS 'adopter_role';
DROP ROLE IF EXISTS 'general_role';

-- ================== CREATING ROLES ==================
CREATE ROLE IF NOT EXISTS 'admin_role';
CREATE ROLE IF NOT EXISTS 'shelter_worker_role';
CREATE ROLE IF NOT EXISTS 'adopter_role';
CREATE ROLE IF NOT EXISTS 'general_role';

-- ============ GRANTING PRIVILEGES TO ROLES ============

-- 1. Administrators have full system control
GRANT ALL PRIVILEGES ON pet_adoption_db.* TO 'admin_role' WITH GRANT OPTION;

-- 2. Shelter workers manage animals, shelters, and adoption applications
GRANT SELECT, INSERT, UPDATE, DELETE ON pet_adoption_db.Pet TO 'shelter_worker_role';
GRANT SELECT, INSERT, UPDATE, DELETE ON pet_adoption_db.PetType TO 'shelter_worker_role';
GRANT SELECT, INSERT, UPDATE, DELETE ON pet_adoption_db.Shelter TO 'shelter_worker_role';
GRANT SELECT, INSERT, UPDATE ON pet_adoption_db.ShelterWorker TO 'shelter_worker_role';
GRANT SELECT, INSERT, UPDATE, DELETE ON pet_adoption_db.AdoptionApplication TO 'shelter_worker_role';
GRANT SELECT, UPDATE ON pet_adoption_db.Payment TO 'shelter_worker_role';
GRANT SELECT ON pet_adoption_db.User TO 'shelter_worker_role';
GRANT SELECT ON pet_adoption_db.Review TO 'shelter_worker_role';

-- 3. Registered adopters can browse pets, manage applications, and maintain their profile
GRANT SELECT ON pet_adoption_db.Pet TO 'adopter_role';
GRANT SELECT ON pet_adoption_db.PetType TO 'adopter_role';
GRANT SELECT ON pet_adoption_db.Shelter TO 'adopter_role';
GRANT SELECT ON pet_adoption_db.AvailablePets TO 'adopter_role';
GRANT SELECT, INSERT, UPDATE ON pet_adoption_db.AdoptionApplication TO 'adopter_role';
GRANT INSERT ON pet_adoption_db.Payment TO 'adopter_role';
GRANT INSERT ON pet_adoption_db.Review TO 'adopter_role';
GRANT SELECT, UPDATE ON pet_adoption_db.User TO 'adopter_role';

-- 4. General/public users can only view the available pets list
GRANT SELECT ON pet_adoption_db.AvailablePets TO 'general_role';
GRANT SELECT ON pet_adoption_db.Pet TO 'general_role';

-- ============ SAMPLE DATABASE USERS & ROLE ASSIGNMENTS ============
CREATE USER IF NOT EXISTS 'admin_app'@'%' IDENTIFIED BY 'Admin#Pass123';
CREATE USER IF NOT EXISTS 'shelter_app'@'%' IDENTIFIED BY 'Shelter#Pass123';
CREATE USER IF NOT EXISTS 'adopter_app'@'%' IDENTIFIED BY 'Adopter#Pass123';
CREATE USER IF NOT EXISTS 'guest_app'@'%' IDENTIFIED BY 'Guest#Pass123';

GRANT 'admin_role' TO 'admin_app'@'%';
GRANT 'shelter_worker_role' TO 'shelter_app'@'%';
GRANT 'adopter_role' TO 'adopter_app'@'%';
GRANT 'general_role' TO 'guest_app'@'%';

SET DEFAULT ROLE 'admin_role' TO 'admin_app'@'%';
SET DEFAULT ROLE 'shelter_worker_role' TO 'shelter_app'@'%';
SET DEFAULT ROLE 'adopter_role' TO 'adopter_app'@'%';
SET DEFAULT ROLE 'general_role' TO 'guest_app'@'%';