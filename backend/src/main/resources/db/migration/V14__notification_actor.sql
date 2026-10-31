ALTER TABLE user_notification ADD COLUMN actor_id BIGINT NULL,ADD CONSTRAINT fk_notification_actor FOREIGN KEY(actor_id) REFERENCES app_user(id);
UPDATE user_notification n JOIN private_message m ON m.id=n.message_id SET n.actor_id=m.sender_id WHERE n.kind='CHAT';
