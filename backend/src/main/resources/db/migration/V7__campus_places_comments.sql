CREATE TABLE campus_place(id BIGINT PRIMARY KEY AUTO_INCREMENT,name VARCHAR(120) NOT NULL UNIQUE,description VARCHAR(500) NOT NULL);
INSERT INTO campus_place(name,description) VALUES ('计算机科学与技术学院','校园学习与交流地点'),('生命科学学院','校园学习与交流地点'),('阅海居B2','校园宿舍生活交流');
CREATE TABLE place_comment(id BIGINT PRIMARY KEY AUTO_INCREMENT,place_id BIGINT NOT NULL,user_id BIGINT NOT NULL,content VARCHAR(1000) NOT NULL,created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(place_id) REFERENCES campus_place(id),FOREIGN KEY(user_id) REFERENCES app_user(id),INDEX idx_place_comment(place_id,id));
