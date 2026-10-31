package cn.edu.sdu.smartlife;
import java.security.Principal;
import java.util.List;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import org.apache.ibatis.annotations.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;
@RestController
@RequestMapping("/api/campus/places")
public class CampusController {
 private final CampusMapper mapper;private final UserMapper users;
 public CampusController(CampusMapper mapper,UserMapper users){this.mapper=mapper;this.users=users;}
 public record Place(long id,String name,String description){}
 public record Comment(long id,String username,String content,String createdAt){}
 public record Input(@NotBlank @Size(max=1000) String content){}
 @GetMapping public List<Place> places(){return mapper.places();}
 private void require(long id){if(mapper.exists(id)==0)throw new ResponseStatusException(HttpStatus.NOT_FOUND);}
 @GetMapping("/{id}/comments") public List<Comment> comments(@PathVariable long id,@RequestParam(defaultValue="0") long before){require(id);if(before<0)throw new ResponseStatusException(HttpStatus.BAD_REQUEST);return mapper.comments(id,before);}
 @PostMapping("/{id}/comments") @ResponseStatus(HttpStatus.CREATED) public void add(@PathVariable long id,@Valid @RequestBody Input input,Principal p){require(id);mapper.add(id,users.find(p.getName()).id(),input.content().trim());}
 @DeleteMapping("/{id}/comments/{commentId}") @ResponseStatus(HttpStatus.NO_CONTENT) public void delete(@PathVariable long id,@PathVariable long commentId,Principal p){if(mapper.delete(id,commentId,users.find(p.getName()).id())!=1)throw new ResponseStatusException(HttpStatus.NOT_FOUND);}
}
@Mapper
interface CampusMapper {
 @Select("SELECT id,name,description FROM campus_place ORDER BY id") List<CampusController.Place> places();
 @Select("SELECT COUNT(*) FROM campus_place WHERE id=#{id}") int exists(long id);
 @Select("SELECT c.id,u.username,c.content,CAST(c.created_at AS CHAR) AS createdAt FROM place_comment c JOIN app_user u ON u.id=c.user_id WHERE c.place_id=#{id} AND (#{before}=0 OR c.id<#{before}) ORDER BY c.id DESC LIMIT 20") List<CampusController.Comment> comments(@Param("id") long id,@Param("before") long before);
 @Insert("INSERT INTO place_comment(place_id,user_id,content) VALUES(#{id},#{user},#{content})") void add(@Param("id") long id,@Param("user") long user,@Param("content") String content);
 @Delete("DELETE FROM place_comment WHERE id=#{comment} AND place_id=#{id} AND user_id=#{user}") int delete(@Param("id") long id,@Param("comment") long comment,@Param("user") long user);
}
