package cn.edu.sdu.smartlife;
import org.apache.ibatis.annotations.*;
@Mapper
public interface ProductImageMapper {
 @Insert("INSERT INTO product_image(product_id,content_type,data) VALUES(#{id},'image/png',#{data}) ON DUPLICATE KEY UPDATE content_type='image/png',data=VALUES(data)") void save(@Param("id") long id,@Param("data") byte[] data);
 record StoredImage(String contentType,byte[] data){}
 @Select("SELECT content_type AS contentType,data FROM product_image WHERE product_id=#{id}") StoredImage find(long id);
}
