CREATE DATABASE IF NOT EXISTS inventory_system
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE inventory_system;

CREATE TABLE users (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  firebase_uid VARCHAR(128) NULL,
  name VARCHAR(150) NOT NULL,
  username VARCHAR(80) NOT NULL,
  email VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NULL,
  bio TEXT NULL,
  photo_url LONGTEXT NULL,
  github_url VARCHAR(255) NULL,
  linkedin_url VARCHAR(255) NULL,
  twitter_url VARCHAR(255) NULL,
  facebook_url VARCHAR(255) NULL,
  instagram_url VARCHAR(255) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_users_username (username),
  UNIQUE KEY uq_users_email (email),
  UNIQUE KEY uq_users_firebase_uid (firebase_uid)
) ENGINE=InnoDB;

CREATE TABLE projects (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  title VARCHAR(180) NOT NULL,
  description TEXT NULL,
  status ENUM('Completed', 'In Progress', 'Planned') NOT NULL DEFAULT 'Planned',
  project_link VARCHAR(255) NULL,
  sort_order INT UNSIGNED NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_projects_user_id (user_id),
  KEY idx_projects_status (status),
  CONSTRAINT fk_projects_user
    FOREIGN KEY (user_id) REFERENCES users (id)
    ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE project_tags (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  project_id BIGINT UNSIGNED NOT NULL,
  tag_name VARCHAR(80) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_project_tags_project_tag (project_id, tag_name),
  CONSTRAINT fk_project_tags_project
    FOREIGN KEY (project_id) REFERENCES projects (id)
    ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE skills (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  title VARCHAR(120) NOT NULL,
  level ENUM('Beginner', 'Intermediate', 'Advanced') NOT NULL DEFAULT 'Beginner',
  percent TINYINT UNSIGNED NOT NULL DEFAULT 0,
  sort_order INT UNSIGNED NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_skills_user_id (user_id),
  CONSTRAINT fk_skills_user
    FOREIGN KEY (user_id) REFERENCES users (id)
    ON DELETE CASCADE,
  CONSTRAINT chk_skills_percent
    CHECK (percent <= 100)
) ENGINE=InnoDB;

CREATE VIEW public_portfolios AS
SELECT
  id,
  name,
  username,
  bio,
  photo_url,
  github_url,
  linkedin_url,
  twitter_url,
  facebook_url,
  instagram_url,
  created_at
FROM users;

