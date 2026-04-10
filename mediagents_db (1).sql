-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 07, 2026 at 05:48 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `mediagents_db`
--
CREATE DATABASE IF NOT EXISTS `mediagents_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `mediagents_db`;

-- --------------------------------------------------------

--
-- Table structure for table `agent_events`
--

DROP TABLE IF EXISTS `agent_events`;
CREATE TABLE `agent_events` (
  `id` bigint(20) NOT NULL,
  `event_name` varchar(100) NOT NULL,
  `publisher_agent` varchar(50) NOT NULL,
  `payload` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`payload`)),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `agent_latency`
--

DROP TABLE IF EXISTS `agent_latency`;
CREATE TABLE `agent_latency` (
  `id` bigint(20) NOT NULL,
  `agent_name` varchar(50) NOT NULL,
  `endpoint` varchar(100) DEFAULT NULL,
  `status_code` int(11) DEFAULT NULL,
  `response_ms` int(11) DEFAULT NULL,
  `triggered_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `alert_acknowledgments`
--

DROP TABLE IF EXISTS `alert_acknowledgments`;
CREATE TABLE `alert_acknowledgments` (
  `id` int(11) NOT NULL,
  `alert_key` varchar(100) NOT NULL,
  `acknowledged_by` varchar(100) DEFAULT NULL,
  `acknowledged_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `alert_thresholds`
--

DROP TABLE IF EXISTS `alert_thresholds`;
CREATE TABLE `alert_thresholds` (
  `id` varchar(50) NOT NULL,
  `label` varchar(100) NOT NULL,
  `unit` varchar(20) DEFAULT NULL,
  `e_min` float DEFAULT NULL,
  `e_max` float DEFAULT NULL,
  `u_min` float DEFAULT NULL,
  `u_max` float DEFAULT NULL,
  `is_enabled` tinyint(1) DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `alert_timeline`
--

DROP TABLE IF EXISTS `alert_timeline`;
CREATE TABLE `alert_timeline` (
  `id` bigint(20) NOT NULL,
  `patient_id` char(36) DEFAULT NULL,
  `alert_type` varchar(50) DEFAULT NULL,
  `severity_score` tinyint(4) DEFAULT NULL,
  `acknowledged` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `appointments`
--

DROP TABLE IF EXISTS `appointments`;
CREATE TABLE `appointments` (
  `id` char(36) NOT NULL,
  `patient_id` char(36) DEFAULT NULL,
  `doctor_id` char(36) DEFAULT NULL,
  `triage_id` char(36) DEFAULT NULL,
  `room_id` char(36) DEFAULT NULL,
  `scheduled_at` datetime NOT NULL,
  `duration_mins` smallint(6) DEFAULT 15,
  `status` enum('scheduled','confirmed','in_progress','completed','cancelled','no_show') DEFAULT 'scheduled',
  `priority_score` decimal(5,2) DEFAULT NULL,
  `est_wait_mins` smallint(6) DEFAULT NULL,
  `cancellation_reason` text DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `audit_log`
--

DROP TABLE IF EXISTS `audit_log`;
CREATE TABLE `audit_log` (
  `id` bigint(20) NOT NULL,
  `event_time` timestamp NOT NULL DEFAULT current_timestamp(),
  `user_id` char(36) DEFAULT NULL,
  `user_role` varchar(20) DEFAULT NULL,
  `action` varchar(50) NOT NULL,
  `resource_type` varchar(50) DEFAULT NULL,
  `resource_id` char(36) DEFAULT NULL,
  `patient_id` char(36) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  `is_anomalous` tinyint(1) DEFAULT 0,
  `details` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`details`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `chat_messages`
--

DROP TABLE IF EXISTS `chat_messages`;
CREATE TABLE `chat_messages` (
  `id` int(11) NOT NULL,
  `patient_id` varchar(36) NOT NULL,
  `role` varchar(20) NOT NULL,
  `content` text NOT NULL,
  `timestamp` datetime DEFAULT NULL,
  `intent` varchar(50) DEFAULT NULL,
  `metadata_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`metadata_json`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `chat_sessions`
--

DROP TABLE IF EXISTS `chat_sessions`;
CREATE TABLE `chat_sessions` (
  `id` char(36) NOT NULL,
  `session_id` char(36) NOT NULL,
  `patient_id` char(36) DEFAULT NULL,
  `messages` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`messages`)),
  `intent_log` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`intent_log`)),
  `language` varchar(10) DEFAULT 'en',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `clinical_notes`
--

DROP TABLE IF EXISTS `clinical_notes`;
CREATE TABLE `clinical_notes` (
  `id` char(36) NOT NULL,
  `patient_id` char(36) DEFAULT NULL,
  `doctor_id` char(36) DEFAULT NULL,
  `appointment_id` char(36) DEFAULT NULL,
  `note_type` enum('SOAP','progress','discharge','referral') DEFAULT 'SOAP',
  `subjective` text DEFAULT NULL,
  `objective` text DEFAULT NULL,
  `assessment` text DEFAULT NULL,
  `plan` text DEFAULT NULL,
  `is_signed` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `diagnoses`
--

DROP TABLE IF EXISTS `diagnoses`;
CREATE TABLE `diagnoses` (
  `id` char(36) NOT NULL,
  `patient_id` char(36) DEFAULT NULL,
  `doctor_id` char(36) DEFAULT NULL,
  `icd10_code` varchar(10) DEFAULT NULL,
  `icd10_description` varchar(255) DEFAULT NULL,
  `status` enum('active','resolved','chronic','ruled_out') DEFAULT 'active',
  `onset_date` date DEFAULT NULL,
  `resolved_date` date DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `doctor_leaves`
--

DROP TABLE IF EXISTS `doctor_leaves`;
CREATE TABLE `doctor_leaves` (
  `id` char(36) NOT NULL,
  `doctor_id` char(36) DEFAULT NULL,
  `leave_start` datetime NOT NULL,
  `leave_end` datetime NOT NULL,
  `reason` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `doctor_schedules`
--

DROP TABLE IF EXISTS `doctor_schedules`;
CREATE TABLE `doctor_schedules` (
  `id` char(36) NOT NULL,
  `doctor_id` char(36) DEFAULT NULL,
  `day_of_week` tinyint(4) DEFAULT NULL CHECK (`day_of_week` >= 0 and `day_of_week` <= 6),
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  `is_active` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `escalation_rules`
--

DROP TABLE IF EXISTS `escalation_rules`;
CREATE TABLE `escalation_rules` (
  `id` int(11) NOT NULL,
  `rule_text` varchar(255) NOT NULL,
  `action_text` varchar(255) NOT NULL,
  `status` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `generated_reports`
--

DROP TABLE IF EXISTS `generated_reports`;
CREATE TABLE `generated_reports` (
  `id` varchar(36) NOT NULL,
  `title` varchar(255) NOT NULL,
  `type` varchar(50) NOT NULL,
  `size` varchar(20) NOT NULL,
  `format` varchar(10) NOT NULL,
  `status` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`data`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `health_records`
--

DROP TABLE IF EXISTS `health_records`;
CREATE TABLE `health_records` (
  `id` varchar(36) NOT NULL,
  `patient_id` varchar(36) NOT NULL,
  `doctor_id` varchar(100) DEFAULT NULL,
  `note_type` varchar(50) DEFAULT NULL,
  `subjective` text DEFAULT NULL,
  `objective` text DEFAULT NULL,
  `assessment` text DEFAULT NULL,
  `plan` text DEFAULT NULL,
  `free_text` text DEFAULT NULL,
  `is_signed` tinyint(1) DEFAULT 0,
  `signed_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `imaging_reports`
--

DROP TABLE IF EXISTS `imaging_reports`;
CREATE TABLE `imaging_reports` (
  `id` char(36) NOT NULL,
  `patient_id` char(36) DEFAULT NULL,
  `modality` varchar(50) DEFAULT NULL,
  `body_part` varchar(100) DEFAULT NULL,
  `radiologist_notes` text DEFAULT NULL,
  `ai_annotation` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`ai_annotation`)),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `lab_documents`
--

DROP TABLE IF EXISTS `lab_documents`;
CREATE TABLE `lab_documents` (
  `id` char(36) NOT NULL,
  `patient_id` char(36) DEFAULT NULL,
  `file_url` text DEFAULT NULL,
  `ocr_text` text DEFAULT NULL,
  `extracted_values` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`extracted_values`)),
  `uploaded_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `lab_orders`
--

DROP TABLE IF EXISTS `lab_orders`;
CREATE TABLE `lab_orders` (
  `id` char(36) NOT NULL,
  `patient_id` char(36) DEFAULT NULL,
  `doctor_id` char(36) DEFAULT NULL,
  `test_name` varchar(200) NOT NULL,
  `loinc_code` varchar(20) DEFAULT NULL,
  `status` enum('ordered','collected','processing','resulted','cancelled') DEFAULT 'ordered',
  `priority` enum('routine','urgent','stat') DEFAULT 'routine',
  `ordered_at` datetime DEFAULT current_timestamp(),
  `resulted_at` datetime DEFAULT NULL,
  `result_value` decimal(10,4) DEFAULT NULL,
  `result_unit` varchar(30) DEFAULT NULL,
  `result_text` text DEFAULT NULL,
  `reference_range` varchar(50) DEFAULT NULL,
  `is_abnormal` tinyint(1) DEFAULT 0,
  `result_narrative` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `medication_doses`
--

DROP TABLE IF EXISTS `medication_doses`;
CREATE TABLE `medication_doses` (
  `id` bigint(20) NOT NULL,
  `patient_id` char(36) DEFAULT NULL,
  `drug_code` varchar(50) DEFAULT NULL,
  `scheduled_time` datetime DEFAULT NULL,
  `dose_taken` tinyint(1) DEFAULT 0,
  `taken_at` datetime DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
CREATE TABLE `notifications` (
  `id` char(36) NOT NULL,
  `patient_id` char(36) DEFAULT NULL,
  `channel` enum('push','sms','email','in_app') NOT NULL,
  `event_type` varchar(50) DEFAULT NULL,
  `subject` varchar(200) DEFAULT NULL,
  `body` text DEFAULT NULL,
  `status` enum('queued','sent','delivered','failed') DEFAULT 'queued',
  `external_id` varchar(100) DEFAULT NULL,
  `sent_at` datetime DEFAULT NULL,
  `read_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `patients`
--

DROP TABLE IF EXISTS `patients`;
CREATE TABLE `patients` (
  `id` char(36) NOT NULL,
  `mrn` varchar(20) NOT NULL,
  `first_name_enc` blob NOT NULL,
  `last_name_enc` blob NOT NULL,
  `dob_enc` blob NOT NULL,
  `gender` enum('male','female','other','unknown') DEFAULT 'unknown',
  `language_pref` varchar(10) DEFAULT 'en',
  `phone_enc` blob DEFAULT NULL,
  `email_enc` blob DEFAULT NULL,
  `address_enc` blob DEFAULT NULL,
  `blood_group` varchar(5) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `pref_health_updates` tinyint(1) DEFAULT 1,
  `pref_appointments` tinyint(1) DEFAULT 1,
  `pref_medication` tinyint(1) DEFAULT 1,
  `height` varchar(50) DEFAULT NULL,
  `weight` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `patient_vitals`
--

DROP TABLE IF EXISTS `patient_vitals`;
CREATE TABLE `patient_vitals` (
  `id` bigint(20) NOT NULL,
  `patient_id` char(36) DEFAULT NULL,
  `device_id` varchar(100) DEFAULT NULL,
  `source` varchar(20) DEFAULT NULL,
  `hr` decimal(5,2) DEFAULT NULL,
  `bp_sys` decimal(5,2) DEFAULT NULL,
  `bp_dia` decimal(5,2) DEFAULT NULL,
  `spo2` decimal(5,2) DEFAULT NULL,
  `temp_c` decimal(5,2) DEFAULT NULL,
  `rr` decimal(5,2) DEFAULT NULL,
  `glucose` decimal(5,2) DEFAULT NULL,
  `news2_score` tinyint(4) DEFAULT 0,
  `measured_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `prescriptions`
--

DROP TABLE IF EXISTS `prescriptions`;
CREATE TABLE `prescriptions` (
  `id` char(36) NOT NULL,
  `patient_id` char(36) DEFAULT NULL,
  `doctor_id` char(36) DEFAULT NULL,
  `drug_name` varchar(200) NOT NULL,
  `drug_code` varchar(50) DEFAULT NULL,
  `dosage` varchar(100) DEFAULT NULL,
  `frequency` varchar(100) DEFAULT NULL,
  `route` varchar(50) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `status` enum('active','completed','discontinued','on_hold') DEFAULT 'active',
  `adherence_score` decimal(5,2) DEFAULT 100.00,
  `refill_due_date` date DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `refill_requests`
--

DROP TABLE IF EXISTS `refill_requests`;
CREATE TABLE `refill_requests` (
  `id` varchar(36) NOT NULL,
  `patient_id` varchar(36) NOT NULL,
  `drug_name` varchar(200) NOT NULL,
  `status` enum('pending','approved','rejected') DEFAULT NULL,
  `requested_at` datetime DEFAULT NULL,
  `processed_at` datetime DEFAULT NULL,
  `notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `risk_scores`
--

DROP TABLE IF EXISTS `risk_scores`;
CREATE TABLE `risk_scores` (
  `id` char(36) NOT NULL,
  `patient_id` char(36) DEFAULT NULL,
  `scored_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `deterioration_pct` decimal(5,2) DEFAULT NULL,
  `readmission_pct` decimal(5,2) DEFAULT NULL,
  `emergency_pct` decimal(5,2) DEFAULT NULL,
  `risk_tier` enum('Low','Medium','High','Critical') DEFAULT NULL,
  `top_risk_factors` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`top_risk_factors`)),
  `recommended_intervention` text DEFAULT NULL,
  `model_version` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `rooms`
--

DROP TABLE IF EXISTS `rooms`;
CREATE TABLE `rooms` (
  `id` char(36) NOT NULL,
  `name` varchar(50) NOT NULL,
  `type` enum('consultation','procedure','emergency','waiting') NOT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `equipment` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`equipment`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `staff`
--

DROP TABLE IF EXISTS `staff`;
CREATE TABLE `staff` (
  `id` char(36) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `role` enum('patient','doctor','nurse','admin','radiologist','dentist') NOT NULL,
  `speciality` varchar(100) DEFAULT NULL,
  `license_number` varchar(50) DEFAULT NULL,
  `is_on_duty` tinyint(1) DEFAULT 0,
  `is_busy` tinyint(1) DEFAULT 0,
  `fcm_token` text DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `system_config`
--

DROP TABLE IF EXISTS `system_config`;
CREATE TABLE `system_config` (
  `key` varchar(100) NOT NULL,
  `value` text NOT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `triage_records`
--

DROP TABLE IF EXISTS `triage_records`;
CREATE TABLE `triage_records` (
  `id` varchar(36) NOT NULL,
  `patient_id` varchar(36) DEFAULT NULL,
  `session_id` varchar(36) NOT NULL,
  `symptom_text` text DEFAULT NULL,
  `duration` varchar(100) DEFAULT NULL,
  `severity_score` int(11) DEFAULT NULL,
  `urgency_tier` enum('Emergency','Urgent','Routine','Self-care') NOT NULL,
  `reasoning` text DEFAULT NULL,
  `recommended_action` text DEFAULT NULL,
  `icd10_hints` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`icd10_hints`)),
  `drug_alerts` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`drug_alerts`)),
  `assigned_doctor` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `medication_analysis` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`medication_analysis`)),
  `decision_support` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`decision_support`)),
  `ehr_sync_status` varchar(50) DEFAULT NULL,
  `risk_analysis` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`risk_analysis`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` char(36) NOT NULL,
  `patient_id` char(36) DEFAULT NULL,
  `staff_id` char(36) DEFAULT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `keycloak_id` varchar(64) DEFAULT NULL,
  `role` enum('patient','doctor','nurse','admin','radiologist','dentist') NOT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `last_login` datetime DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `vital_alerts`
--

DROP TABLE IF EXISTS `vital_alerts`;
CREATE TABLE `vital_alerts` (
  `id` char(36) NOT NULL,
  `patient_id` char(36) DEFAULT NULL,
  `alert_type` enum('vital_critical','triage_emergency','risk_critical','chat_emergency','medication_missed') NOT NULL,
  `severity` enum('URGENT','CRITICAL') NOT NULL,
  `message_doctor` varchar(280) DEFAULT NULL,
  `message_patient` text DEFAULT NULL,
  `vital_name` varchar(50) DEFAULT NULL,
  `vital_value` decimal(10,4) DEFAULT NULL,
  `assigned_doctor_id` char(36) DEFAULT NULL,
  `acknowledged_at` datetime DEFAULT NULL,
  `escalated_at` datetime DEFAULT NULL,
  `resolved_at` datetime DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `agent_events`
--
ALTER TABLE `agent_events`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `agent_latency`
--
ALTER TABLE `agent_latency`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `alert_acknowledgments`
--
ALTER TABLE `alert_acknowledgments`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_alert_acknowledgments_alert_key` (`alert_key`);

--
-- Indexes for table `alert_thresholds`
--
ALTER TABLE `alert_thresholds`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `alert_timeline`
--
ALTER TABLE `alert_timeline`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`);

--
-- Indexes for table `appointments`
--
ALTER TABLE `appointments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `doctor_id` (`doctor_id`),
  ADD KEY `triage_id` (`triage_id`),
  ADD KEY `room_id` (`room_id`);

--
-- Indexes for table `audit_log`
--
ALTER TABLE `audit_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_audit_patient` (`patient_id`);

--
-- Indexes for table `chat_messages`
--
ALTER TABLE `chat_messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_chat_messages_patient_id` (`patient_id`);

--
-- Indexes for table `chat_sessions`
--
ALTER TABLE `chat_sessions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `session_id` (`session_id`),
  ADD KEY `patient_id` (`patient_id`);

--
-- Indexes for table `clinical_notes`
--
ALTER TABLE `clinical_notes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `doctor_id` (`doctor_id`),
  ADD KEY `appointment_id` (`appointment_id`);

--
-- Indexes for table `diagnoses`
--
ALTER TABLE `diagnoses`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `doctor_id` (`doctor_id`);

--
-- Indexes for table `doctor_leaves`
--
ALTER TABLE `doctor_leaves`
  ADD PRIMARY KEY (`id`),
  ADD KEY `doctor_id` (`doctor_id`);

--
-- Indexes for table `doctor_schedules`
--
ALTER TABLE `doctor_schedules`
  ADD PRIMARY KEY (`id`),
  ADD KEY `doctor_id` (`doctor_id`);

--
-- Indexes for table `escalation_rules`
--
ALTER TABLE `escalation_rules`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `generated_reports`
--
ALTER TABLE `generated_reports`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `health_records`
--
ALTER TABLE `health_records`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`);

--
-- Indexes for table `imaging_reports`
--
ALTER TABLE `imaging_reports`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`);

--
-- Indexes for table `lab_documents`
--
ALTER TABLE `lab_documents`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`);

--
-- Indexes for table `lab_orders`
--
ALTER TABLE `lab_orders`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `doctor_id` (`doctor_id`);

--
-- Indexes for table `medication_doses`
--
ALTER TABLE `medication_doses`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`);

--
-- Indexes for table `patients`
--
ALTER TABLE `patients`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `mrn` (`mrn`),
  ADD KEY `idx_patients_mrn` (`mrn`);

--
-- Indexes for table `patient_vitals`
--
ALTER TABLE `patient_vitals`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`,`measured_at`),
  ADD KEY `idx_vitals_patient_time` (`patient_id`,`measured_at`);

--
-- Indexes for table `prescriptions`
--
ALTER TABLE `prescriptions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `doctor_id` (`doctor_id`);

--
-- Indexes for table `refill_requests`
--
ALTER TABLE `refill_requests`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`);

--
-- Indexes for table `risk_scores`
--
ALTER TABLE `risk_scores`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`);

--
-- Indexes for table `rooms`
--
ALTER TABLE `rooms`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `staff`
--
ALTER TABLE `staff`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `system_config`
--
ALTER TABLE `system_config`
  ADD PRIMARY KEY (`key`);

--
-- Indexes for table `triage_records`
--
ALTER TABLE `triage_records`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `keycloak_id` (`keycloak_id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `staff_id` (`staff_id`);

--
-- Indexes for table `vital_alerts`
--
ALTER TABLE `vital_alerts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `assigned_doctor_id` (`assigned_doctor_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `agent_events`
--
ALTER TABLE `agent_events`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `agent_latency`
--
ALTER TABLE `agent_latency`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `alert_acknowledgments`
--
ALTER TABLE `alert_acknowledgments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `alert_timeline`
--
ALTER TABLE `alert_timeline`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `audit_log`
--
ALTER TABLE `audit_log`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `chat_messages`
--
ALTER TABLE `chat_messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `escalation_rules`
--
ALTER TABLE `escalation_rules`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `medication_doses`
--
ALTER TABLE `medication_doses`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `patient_vitals`
--
ALTER TABLE `patient_vitals`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `alert_timeline`
--
ALTER TABLE `alert_timeline`
  ADD CONSTRAINT `alert_timeline_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `appointments`
--
ALTER TABLE `appointments`
  ADD CONSTRAINT `appointments_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `appointments_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `staff` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `appointments_ibfk_3` FOREIGN KEY (`triage_id`) REFERENCES `triage_records` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `appointments_ibfk_4` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `chat_sessions`
--
ALTER TABLE `chat_sessions`
  ADD CONSTRAINT `chat_sessions_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `clinical_notes`
--
ALTER TABLE `clinical_notes`
  ADD CONSTRAINT `clinical_notes_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `clinical_notes_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `staff` (`id`),
  ADD CONSTRAINT `clinical_notes_ibfk_3` FOREIGN KEY (`appointment_id`) REFERENCES `appointments` (`id`);

--
-- Constraints for table `diagnoses`
--
ALTER TABLE `diagnoses`
  ADD CONSTRAINT `diagnoses_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `diagnoses_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `staff` (`id`);

--
-- Constraints for table `doctor_leaves`
--
ALTER TABLE `doctor_leaves`
  ADD CONSTRAINT `doctor_leaves_ibfk_1` FOREIGN KEY (`doctor_id`) REFERENCES `staff` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `doctor_schedules`
--
ALTER TABLE `doctor_schedules`
  ADD CONSTRAINT `doctor_schedules_ibfk_1` FOREIGN KEY (`doctor_id`) REFERENCES `staff` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `imaging_reports`
--
ALTER TABLE `imaging_reports`
  ADD CONSTRAINT `imaging_reports_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `lab_documents`
--
ALTER TABLE `lab_documents`
  ADD CONSTRAINT `lab_documents_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `lab_orders`
--
ALTER TABLE `lab_orders`
  ADD CONSTRAINT `lab_orders_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `lab_orders_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `staff` (`id`);

--
-- Constraints for table `medication_doses`
--
ALTER TABLE `medication_doses`
  ADD CONSTRAINT `medication_doses_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `patient_vitals`
--
ALTER TABLE `patient_vitals`
  ADD CONSTRAINT `patient_vitals_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `prescriptions`
--
ALTER TABLE `prescriptions`
  ADD CONSTRAINT `prescriptions_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `prescriptions_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `staff` (`id`);

--
-- Constraints for table `refill_requests`
--
ALTER TABLE `refill_requests`
  ADD CONSTRAINT `refill_requests_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`);

--
-- Constraints for table `risk_scores`
--
ALTER TABLE `risk_scores`
  ADD CONSTRAINT `risk_scores_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `triage_records`
--
ALTER TABLE `triage_records`
  ADD CONSTRAINT `triage_records_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`);

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `users_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `users_ibfk_2` FOREIGN KEY (`staff_id`) REFERENCES `staff` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `vital_alerts`
--
ALTER TABLE `vital_alerts`
  ADD CONSTRAINT `vital_alerts_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `vital_alerts_ibfk_2` FOREIGN KEY (`assigned_doctor_id`) REFERENCES `staff` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
