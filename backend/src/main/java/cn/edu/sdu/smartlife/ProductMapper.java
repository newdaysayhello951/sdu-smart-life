package cn.edu.sdu.smartlife;
import java.math.BigDecimal;
import java.util.List;
import org.apache.ibatis.annotations.*;
@Mapper
public interface ProductMapper {
 @Insert("INSERT INTO product(title,description,price,location,image_url,owner_id) VALUES(#{title},#{description},#{price},#{location},'/assets/legacy/images/default.jpg',#{owner})")
 void create(@Param("title") String title,@Param("description") String description,@Param("price") BigDecimal price,@Param("location") String location,@Param("owner") Long owner);
 @Select("SELECT id,title,description,price,location,image_url AS imageUrl,status FROM product WHERE owner_id=#{owner} ORDER BY id DESC") List<Product> mine(Long owner);
 @Update("UPDATE product SET status='WITHDRAWN' WHERE id=#{id} AND owner_id=#{owner} AND status='AVAILABLE'") int withdraw(@Param("id") long id,@Param("owner") long owner);
 @Update("UPDATE product SET title=#{title},description=#{description},price=#{price},location=#{location} WHERE id=#{id} AND owner_id=#{owner} AND status='AVAILABLE'")
 int edit(@Param("id") long id,@Param("owner") long owner,@Param("title") String title,@Param("description") String description,@Param("price") BigDecimal price,@Param("location") String location);
 @Update("UPDATE product SET image_url=#{url} WHERE id=#{id} AND owner_id=#{owner} AND status='AVAILABLE'") int image(@Param("id") long id,@Param("owner") long owner,@Param("url") String url);
 @Select("SELECT COUNT(*) FROM product WHERE id=#{id} AND owner_id=#{owner} AND status='AVAILABLE'") int owned(@Param("id") long id,@Param("owner") long owner);
 record Product(Long id,String title,String description,BigDecimal price,String location,String imageUrl,String status){}
 @Select("<script>SELECT id,title,description,price,location,image_url AS imageUrl,status FROM product WHERE status='AVAILABLE' <if test='keyword != null and keyword != &quot;&quot;'>AND (LOCATE(#{keyword},title)>0 OR LOCATE(#{keyword},description)>0)</if> ORDER BY id DESC LIMIT #{limit} OFFSET #{offset}</script>")
 List<Product> list(@Param("keyword") String keyword,@Param("limit") int limit,@Param("offset") int offset);
 @Select("<script>SELECT COUNT(*) FROM product WHERE status='AVAILABLE' <if test='keyword != null and keyword != &quot;&quot;'>AND (LOCATE(#{keyword},title)>0 OR LOCATE(#{keyword},description)>0)</if></script>")
 long count(@Param("keyword") String keyword);
 @Select("SELECT id,title,description,price,location,image_url AS imageUrl,status FROM product WHERE id=#{id}") Product find(long id);
}
