package cn.edu.sdu.smartlife;
import org.apache.ibatis.annotations.*;
@Mapper
public interface UserMapper {
 @Select("SELECT id, username, password_hash AS passwordHash FROM app_user WHERE username=#{username}") Account find(String username);
 @Insert("INSERT INTO app_user(username,password_hash) VALUES(#{username},#{passwordHash})") void insert(Account account);
 @Select("SELECT id,username,password_hash AS passwordHash FROM app_user WHERE id=#{id}") Account findId(long id);
 record Account(Long id,String username,String passwordHash) {}
}
