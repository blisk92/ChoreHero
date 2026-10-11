-- ChoreHero v1 — initial schema (MariaDB 11)
-- Generated to match prisma/schema.prisma. Apply via `prisma migrate deploy`.
-- Domain vocabulary follows CONTEXT.md exactly. ADR-0001: kid identity is
-- KidDevice.device_token_hash — no child auth row exists.

-- ---------------------------------------------------------------------------
CREATE TABLE `household` (
  `id`         VARCHAR(30)  NOT NULL,
  `name`       VARCHAR(191) NULL,
  `timezone`   VARCHAR(64)  NOT NULL DEFAULT 'UTC',
  `created_at` DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
CREATE TABLE `parent` (
  `id`               VARCHAR(30)  NOT NULL,
  `household_id`     VARCHAR(30)  NOT NULL,
  `email`            VARCHAR(191) NOT NULL,
  `password_hash`    VARCHAR(191) NULL,
  `oauth_provider`   VARCHAR(64)  NULL,
  `oauth_subject`    VARCHAR(191) NULL,
  `created_at`       DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `name`             VARCHAR(191) NULL,
  `name_updated_at`  DATETIME(3)  NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `parent_email_key` (`email`),
  KEY `parent_household_id_idx` (`household_id`),
  CONSTRAINT `parent_household_id_fkey`
    FOREIGN KEY (`household_id`) REFERENCES `household`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
CREATE TABLE `child` (
  `id`                     VARCHAR(30)  NOT NULL,
  `household_id`           VARCHAR(30)  NOT NULL,
  `name`                   VARCHAR(191) NOT NULL,
  `name_updated_at`        DATETIME(3)  NULL,
  `avatar_id`              VARCHAR(64)  NOT NULL,
  `avatar_id_updated_at`   DATETIME(3)  NULL,
  `created_at`             DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  KEY `child_household_id_idx` (`household_id`),
  CONSTRAINT `child_household_id_fkey`
    FOREIGN KEY (`household_id`) REFERENCES `household`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
CREATE TABLE `kid_device` (
  `id`                        VARCHAR(30)  NOT NULL,
  `child_id`                  VARCHAR(30)  NOT NULL,
  `household_id`              VARCHAR(30)  NOT NULL,
  `device_token_hash`         VARCHAR(191) NOT NULL,
  `friendly_name`             VARCHAR(191) NOT NULL,
  `friendly_name_updated_at`  DATETIME(3)  NULL,
  `installed_at`              DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `last_seen_at`              DATETIME(3)  NULL,
  `revoked_at`                DATETIME(3)  NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `kid_device_device_token_hash_key` (`device_token_hash`),
  KEY `kid_device_household_id_idx` (`household_id`),
  KEY `kid_device_child_id_idx` (`child_id`),
  CONSTRAINT `kid_device_child_id_fkey`
    FOREIGN KEY (`child_id`) REFERENCES `child`(`id`) ON DELETE CASCADE,
  CONSTRAINT `kid_device_household_id_fkey`
    FOREIGN KEY (`household_id`) REFERENCES `household`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
CREATE TABLE `household_code` (
  `household_id`   VARCHAR(30)  NOT NULL,
  `code_hash`      VARCHAR(191) NOT NULL,
  `created_at`     DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `regenerated_at` DATETIME(3)  NULL,
  PRIMARY KEY (`household_id`),
  CONSTRAINT `household_code_household_id_fkey`
    FOREIGN KEY (`household_id`) REFERENCES `household`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
CREATE TABLE `chore` (
  `id`                              VARCHAR(30)  NOT NULL,
  `household_id`                    VARCHAR(30)  NOT NULL,
  `name`                            VARCHAR(191) NOT NULL,
  `point_value`                     INT          NOT NULL,
  `review_flagged`                  BOOLEAN      NOT NULL DEFAULT FALSE,
  `kind`                            VARCHAR(16)  NOT NULL,
  `due_at`                          DATETIME(3)  NULL,
  `status`                           VARCHAR(16)  NOT NULL DEFAULT 'pool',
  `claimed_by_child_id`             VARCHAR(30)  NULL,
  `claimed_at`                      DATETIME(3)  NULL,
  `created_at`                      DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `archived_at`                     DATETIME(3)  NULL,

  `name_updated_at`                 DATETIME(3)  NULL,
  `point_value_updated_at`          DATETIME(3)  NULL,
  `review_flagged_updated_at`       DATETIME(3)  NULL,
  `kind_updated_at`                 DATETIME(3)  NULL,
  `due_at_updated_at`               DATETIME(3)  NULL,
  `status_updated_at`               DATETIME(3)  NULL,
  `claimed_by_child_id_updated_at`  DATETIME(3)  NULL,
  `claimed_at_updated_at`           DATETIME(3)  NULL,
  `archived_at_updated_at`          DATETIME(3)  NULL,

  PRIMARY KEY (`id`),
  KEY `chore_household_id_status_idx` (`household_id`, `status`),
  KEY `chore_household_id_kind_status_idx` (`household_id`, `kind`, `status`),
  CONSTRAINT `chore_household_id_fkey`
    FOREIGN KEY (`household_id`) REFERENCES `household`(`id`) ON DELETE CASCADE,
  CONSTRAINT `chore_claimed_by_child_id_fkey`
    FOREIGN KEY (`claimed_by_child_id`) REFERENCES `child`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
CREATE TABLE `streak` (
  `chore_id`                        VARCHAR(30)  NOT NULL,
  `current_length`                  INT          NOT NULL DEFAULT 0,
  `longest_length`                  INT          NOT NULL DEFAULT 0,
  `last_completed_on`               DATE         NULL,

  `current_length_updated_at`       DATETIME(3)  NULL,
  `longest_length_updated_at`       DATETIME(3)  NULL,
  `last_completed_on_updated_at`    DATETIME(3)  NULL,

  PRIMARY KEY (`chore_id`),
  CONSTRAINT `streak_chore_id_fkey`
    FOREIGN KEY (`chore_id`) REFERENCES `chore`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
CREATE TABLE `reward` (
  `id`                          VARCHAR(30)  NOT NULL,
  `household_id`                VARCHAR(30)  NOT NULL,
  `name`                        VARCHAR(191) NOT NULL,
  `point_cost`                  INT          NOT NULL,
  `description`                 TEXT         NULL,
  `stock_remaining`             INT          NULL,

  `name_updated_at`             DATETIME(3)  NULL,
  `point_cost_updated_at`       DATETIME(3)  NULL,
  `description_updated_at`      DATETIME(3)  NULL,
  `stock_remaining_updated_at`  DATETIME(3)  NULL,

  `created_at`                  DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  KEY `reward_household_id_idx` (`household_id`),
  CONSTRAINT `reward_household_id_fkey`
    FOREIGN KEY (`household_id`) REFERENCES `household`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
CREATE TABLE `redemption` (
  `id`                          VARCHAR(30)  NOT NULL,
  `household_id`                VARCHAR(30)  NOT NULL,
  `child_id`                    VARCHAR(30)  NOT NULL,
  `reward_id`                   VARCHAR(30)  NOT NULL,
  `status`                      VARCHAR(16)  NOT NULL DEFAULT 'pending',
  `requested_at`                DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `resolved_at`                 DATETIME(3)  NULL,
  `denial_reason`               TEXT         NULL,

  `status_updated_at`           DATETIME(3)  NULL,
  `resolved_at_updated_at`      DATETIME(3)  NULL,
  `denial_reason_updated_at`    DATETIME(3)  NULL,

  PRIMARY KEY (`id`),
  KEY `redemption_household_id_status_idx` (`household_id`, `status`),
  CONSTRAINT `redemption_household_id_fkey`
    FOREIGN KEY (`household_id`) REFERENCES `household`(`id`) ON DELETE CASCADE,
  CONSTRAINT `redemption_child_id_fkey`
    FOREIGN KEY (`child_id`) REFERENCES `child`(`id`) ON DELETE CASCADE,
  CONSTRAINT `redemption_reward_id_fkey`
    FOREIGN KEY (`reward_id`) REFERENCES `reward`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
CREATE TABLE `points_ledger` (
  `id`         VARCHAR(30)  NOT NULL,
  `child_id`   VARCHAR(30)  NOT NULL,
  `delta`      INT          NOT NULL,
  `source`     VARCHAR(16)  NOT NULL,
  `source_id`  VARCHAR(30)  NOT NULL,
  `created_at` DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  KEY `points_ledger_child_id_created_at_idx` (`child_id`, `created_at`),
  CONSTRAINT `points_ledger_child_id_fkey`
    FOREIGN KEY (`child_id`) REFERENCES `child`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
CREATE TABLE `notification` (
  `id`             VARCHAR(30)  NOT NULL,
  `recipient_kind` VARCHAR(16)  NOT NULL,
  `recipient_id`   VARCHAR(30)  NOT NULL,
  `kind`           VARCHAR(64)  NOT NULL,
  `payload_json`   JSON         NOT NULL,
  `read_at`        DATETIME(3)  NULL,
  `created_at`     DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  KEY `notification_recipient_kind_recipient_id_created_at_idx`
    (`recipient_kind`, `recipient_id`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;