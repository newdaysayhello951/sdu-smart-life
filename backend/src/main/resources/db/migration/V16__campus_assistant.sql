CREATE TABLE ai_knowledge_source (
 id BIGINT PRIMARY KEY AUTO_INCREMENT,
 url VARCHAR(700) NOT NULL UNIQUE, title VARCHAR(300) NOT NULL,
 campus VARCHAR(80) NOT NULL, content MEDIUMTEXT NOT NULL,
 content_hash CHAR(64) NOT NULL, fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE ai_knowledge_chunk (
 id CHAR(36) PRIMARY KEY, source_id BIGINT NOT NULL,
 ordinal INT NOT NULL, content TEXT NOT NULL, embedding JSON NOT NULL,
 FOREIGN KEY(source_id) REFERENCES ai_knowledge_source(id) ON DELETE CASCADE,
 UNIQUE KEY uq_ai_chunk(source_id,ordinal)
);
CREATE TABLE ai_conversation (
 id CHAR(36) PRIMARY KEY, user_id BIGINT NOT NULL, title VARCHAR(100) NOT NULL,
 created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
 updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(user_id) REFERENCES app_user(id), INDEX idx_ai_owner(user_id,updated_at)
);
CREATE TABLE ai_message (
 id BIGINT PRIMARY KEY AUTO_INCREMENT, conversation_id CHAR(36) NOT NULL,
 role VARCHAR(12) NOT NULL, content MEDIUMTEXT NOT NULL,
 metadata JSON NOT NULL, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(conversation_id) REFERENCES ai_conversation(id) ON DELETE CASCADE,
 INDEX idx_ai_history(conversation_id,id)
);
