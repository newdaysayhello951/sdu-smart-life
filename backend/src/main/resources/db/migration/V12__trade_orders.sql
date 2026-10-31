CREATE TABLE trade_order (
 id BIGINT PRIMARY KEY AUTO_INCREMENT,
 product_id BIGINT NOT NULL,
 buyer_id BIGINT NOT NULL,
 seller_id BIGINT NOT NULL,
 product_title VARCHAR(120) NOT NULL,
 price DECIMAL(12,2) NOT NULL,
 status VARCHAR(20) NOT NULL DEFAULT 'RESERVED',
 created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
 updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 FOREIGN KEY(product_id) REFERENCES product(id),FOREIGN KEY(buyer_id) REFERENCES app_user(id),FOREIGN KEY(seller_id) REFERENCES app_user(id),
 INDEX idx_buyer_order(buyer_id,id),INDEX idx_seller_order(seller_id,id),INDEX idx_product_order(product_id,id),CHECK(buyer_id<>seller_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
