ALTER TABLE product ADD COLUMN owner_id BIGINT NULL, ADD CONSTRAINT fk_product_owner FOREIGN KEY(owner_id) REFERENCES app_user(id);
