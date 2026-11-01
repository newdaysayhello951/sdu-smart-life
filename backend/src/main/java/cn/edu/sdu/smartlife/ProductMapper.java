package cn.edu.sdu.smartlife;
import java.math.BigDecimal;
import java.util.List;
import org.apache.ibatis.annotations.*;
@Mapper
public interface ProductMapper {
 @Insert("INSERT INTO product(title,description,price,location,image_url,owner_id,listing_type) VALUES(#{title},#{description},#{price},#{location},'/assets/legacy/images/default.jpg',#{owner},#{kind})")
 void create(@Param("title") String title,@Param("description") String description,@Param("price") BigDecimal price,@Param("location") String location,@Param("owner") Long owner,@Param("kind") String kind);
 @Select("SELECT id,title,description,price,location,image_url AS imageUrl,status,owner_id AS ownerId,(SELECT username FROM app_user WHERE id=owner_id) AS ownerName,listing_type AS kind FROM product WHERE owner_id=#{owner} ORDER BY id DESC") List<Product> mine(Long owner);
 @Update("UPDATE product SET status='WITHDRAWN' WHERE id=#{id} AND owner_id=#{owner} AND status='AVAILABLE'") int withdraw(@Param("id") long id,@Param("owner") long owner);
 @Update("UPDATE product SET title=#{title},description=#{description},price=#{price},location=#{location},listing_type=COALESCE(#{kind},listing_type) WHERE id=#{id} AND owner_id=#{owner} AND status='AVAILABLE'")
 int edit(@Param("id") long id,@Param("owner") long owner,@Param("title") String title,@Param("description") String description,@Param("price") BigDecimal price,@Param("location") String location,@Param("kind") String kind);
 @Update("UPDATE product SET image_url=#{url} WHERE id=#{id} AND owner_id=#{owner} AND status='AVAILABLE'") int image(@Param("id") long id,@Param("owner") long owner,@Param("url") String url);
 @Select("SELECT COUNT(*) FROM product WHERE id=#{id} AND owner_id=#{owner} AND status='AVAILABLE'") int owned(@Param("id") long id,@Param("owner") long owner);
 @Select("SELECT LAST_INSERT_ID()") long lastId();
 record Product(Long id,String title,String description,BigDecimal price,String location,String imageUrl,String status,Long ownerId,String ownerName,String kind){}
 @Select("<script>SELECT id,title,description,price,location,image_url AS imageUrl,status,owner_id AS ownerId,(SELECT username FROM app_user WHERE id=owner_id) AS ownerName,listing_type AS kind FROM product WHERE status='AVAILABLE' AND listing_type=#{kind} AND id &lt;= #{snapshot} <if test='keyword != null and keyword != &quot;&quot;'>AND (LOCATE(#{keyword},title)>0 OR LOCATE(#{keyword},description)>0 OR LOCATE(#{keyword},location)>0)</if> ORDER BY id DESC LIMIT #{limit} OFFSET #{offset}</script>")
 List<Product> list(@Param("kind") String kind,@Param("keyword") String keyword,@Param("limit") int limit,@Param("offset") int offset,@Param("snapshot") long snapshot);
 @Select("<script>SELECT COUNT(*) FROM product WHERE status='AVAILABLE' AND listing_type=#{kind} AND id &lt;= #{snapshot} <if test='keyword != null and keyword != &quot;&quot;'>AND (LOCATE(#{keyword},title)>0 OR LOCATE(#{keyword},description)>0 OR LOCATE(#{keyword},location)>0)</if></script>")
 long count(@Param("kind") String kind,@Param("keyword") String keyword,@Param("snapshot") long snapshot);
 @Select("SELECT COALESCE(MAX(id),0) FROM product") long latestId();
 @Select("SELECT id,title,description,price,location,image_url AS imageUrl,status,owner_id AS ownerId,(SELECT username FROM app_user WHERE id=owner_id) AS ownerName,listing_type AS kind FROM product WHERE id=#{id}") Product find(long id);
}
