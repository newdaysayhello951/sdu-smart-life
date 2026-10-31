package cn.edu.sdu.smartlife;
import java.math.BigDecimal;
import java.util.List;
import org.apache.ibatis.annotations.*;
@Mapper
public interface ProductMapper {
 record Product(Long id,String title,String description,BigDecimal price,String location,String imageUrl,String status){}
 @Select("<script>SELECT id,title,description,price,location,image_url AS imageUrl,status FROM product WHERE status='AVAILABLE' <if test='keyword != null and keyword != &quot;&quot;'>AND (LOCATE(#{keyword},title)>0 OR LOCATE(#{keyword},description)>0)</if> ORDER BY id DESC LIMIT #{limit} OFFSET #{offset}</script>")
 List<Product> list(@Param("keyword") String keyword,@Param("limit") int limit,@Param("offset") int offset);
 @Select("<script>SELECT COUNT(*) FROM product WHERE status='AVAILABLE' <if test='keyword != null and keyword != &quot;&quot;'>AND (LOCATE(#{keyword},title)>0 OR LOCATE(#{keyword},description)>0)</if></script>")
 long count(@Param("keyword") String keyword);
 @Select("SELECT id,title,description,price,location,image_url AS imageUrl,status FROM product WHERE id=#{id}") Product find(long id);
}
