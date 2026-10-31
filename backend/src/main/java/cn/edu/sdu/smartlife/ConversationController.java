package cn.edu.sdu.smartlife;
import java.util.*;
import java.io.*;
import java.security.Principal;
import javax.imageio.ImageIO;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import org.apache.ibatis.annotations.*;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.server.ResponseStatusException;
@RestController
@RequestMapping("/api/conversations")
public class ConversationController {
 private final ConversationMapper db;private final UserMapper users;
 public ConversationController(ConversationMapper db,UserMapper users){this.db=db;this.users=users;}
 public record Message(long id,long userId,String username,String content,String createdAt,Long parentId,Long rootId,String mediaUrl,String replyToUsername,long replyCount){}
 public record Thread(Message message,List<Message> replies){}
 public record Input(@Positive long placeId,@NotNull @Size(max=1000) String content,Long parentId){}
 @GetMapping public List<Thread> list(@RequestParam long placeId,@RequestParam(defaultValue="0") long before){if(before<0)throw new ResponseStatusException(HttpStatus.BAD_REQUEST);requirePlace(placeId);return db.roots(placeId,before).stream().map(m->new Thread(m,db.replies(m.id(),0,2))).toList();}
 private void requirePlace(long id){if(db.place(id)==0)throw new ResponseStatusException(HttpStatus.NOT_FOUND);}
 @GetMapping("/{id}") public Thread detail(@PathVariable long id,@RequestParam(defaultValue="0") long after){if(after<0)throw new ResponseStatusException(HttpStatus.BAD_REQUEST);var m=db.find(id);if(m==null||m.parentId()!=null)throw new ResponseStatusException(HttpStatus.NOT_FOUND);return new Thread(m,db.replies(id,after,50));}
 @GetMapping("/{id}/target/{messageId}") @ResponseStatus(HttpStatus.NO_CONTENT)
 public void target(@PathVariable long id,@PathVariable long messageId){var m=db.find(messageId);if(m==null||(m.id()!=id&&!Objects.equals(m.rootId(),id)))throw new ResponseStatusException(HttpStatus.NOT_FOUND);}
 @PostMapping(consumes="multipart/form-data") @ResponseStatus(HttpStatus.CREATED)
 @org.springframework.transaction.annotation.Transactional(rollbackFor=Exception.class)
 public Map<String,Long> add(@Valid @RequestPart("message") Input input,@RequestPart(value="file",required=false) MultipartFile file,Principal principal) throws IOException {
 requirePlace(input.placeId());if(input.content().isBlank()&&(file==null||file.isEmpty()))throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
 Long root=null;if(input.parentId()!=null){var parent=db.find(input.parentId());if(parent==null||db.commentPlace(parent.id())!=input.placeId())throw new ResponseStatusException(HttpStatus.BAD_REQUEST);root=parent.rootId()==null?parent.id():parent.rootId();}
 byte[] bytes=null;String mime=null;
 if(file!=null&&!file.isEmpty()){
  if(file.getSize()>5*1024*1024)throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"附件超过5MB");
  try(var in=ImageIO.createImageInputStream(file.getInputStream())){var readers=ImageIO.getImageReaders(in);if(!readers.hasNext())throw new ResponseStatusException(HttpStatus.BAD_REQUEST);var reader=readers.next();try{reader.setInput(in);String format=reader.getFormatName().toLowerCase();if(!List.of("png","jpeg","gif").contains(format)||(long)reader.getWidth(0)*reader.getHeight(0)>16000000)throw new ResponseStatusException(HttpStatus.BAD_REQUEST);if(format.equals("gif")){if(reader.getNumImages(true)>200)throw new ResponseStatusException(HttpStatus.BAD_REQUEST);bytes=file.getBytes();mime="image/gif";}else{var image=reader.read(0);var out=new ByteArrayOutputStream();ImageIO.write(image,"png",out);bytes=out.toByteArray();mime="image/png";if(bytes.length>16*1024*1024)throw new ResponseStatusException(HttpStatus.BAD_REQUEST);}}finally{reader.dispose();}}
  catch(javax.imageio.IIOException e){throw new ResponseStatusException(HttpStatus.BAD_REQUEST);}
 }
 db.add(input.placeId(),users.find(principal.getName()).id(),input.content().trim(),input.parentId(),root,bytes,mime);long id=db.last();if(input.parentId()!=null){var parent=db.find(input.parentId());long self=users.find(principal.getName()).id();if(parent.userId()!=self)db.notifyReply(parent.userId(),"你的校园发言收到回复","/campus/"+input.placeId()+"/conversations/"+root+"?focus="+id); }return Map.of("id",id,"rootId",root==null?id:root);
 }
 @GetMapping("/{id}/image") public ResponseEntity<byte[]> image(@PathVariable long id){var data=db.media(id);if(data==null||data.data()==null)throw new ResponseStatusException(HttpStatus.NOT_FOUND);return ResponseEntity.ok().cacheControl(CacheControl.noStore()).contentType(MediaType.parseMediaType(data.mime())).header("X-Content-Type-Options","nosniff").body(data.data());}
 @GetMapping("/avatars/{id}") public ResponseEntity<byte[]> avatar(@PathVariable long id) throws IOException{var stored=db.avatar(id);byte[] data=stored==null?null:stored.data();if(data==null){try(var in=getClass().getResourceAsStream("/default-avatar.jpg")){return ResponseEntity.ok().contentType(MediaType.IMAGE_JPEG).cacheControl(CacheControl.noStore()).body(in.readAllBytes());}}return ResponseEntity.ok().contentType(MediaType.IMAGE_PNG).cacheControl(CacheControl.noStore()).body(data);}
}
@Mapper
interface ConversationMapper {
 String C="SELECT c.id,c.user_id AS userId,u.username,c.content,CAST(c.created_at AS CHAR) AS createdAt,c.parent_id AS parentId,c.root_id AS rootId,CASE WHEN c.media IS NULL THEN NULL ELSE CONCAT('/api/conversations/',c.id,'/image') END AS mediaUrl,(SELECT u2.username FROM place_comment p JOIN app_user u2 ON u2.id=p.user_id WHERE p.id=c.parent_id) AS replyToUsername,(SELECT COUNT(*) FROM place_comment r WHERE r.root_id=c.id) AS replyCount FROM place_comment c JOIN app_user u ON u.id=c.user_id ";
 @Select(C+"WHERE c.place_id=#{place} AND c.parent_id IS NULL AND (#{before}=0 OR c.id<#{before}) ORDER BY c.id DESC LIMIT 20") List<ConversationController.Message> roots(@Param("place")long place,@Param("before")long before);
 @Select(C+"WHERE c.root_id=#{root} AND c.id>#{after} ORDER BY c.id ASC LIMIT #{limit}") List<ConversationController.Message> replies(@Param("root")long root,@Param("after")long after,@Param("limit")int limit);
 @Select(C+"WHERE c.id=#{id}") ConversationController.Message find(long id);
 @Select("SELECT COUNT(*) FROM campus_place WHERE id=#{id}") int place(long id);
 @Select("SELECT place_id FROM place_comment WHERE id=#{id}") long commentPlace(long id);
 @Insert("INSERT INTO place_comment(place_id,user_id,content,parent_id,root_id,media,media_type) VALUES(#{place},#{user},#{content},#{parent},#{root},#{bytes},#{mime})") void add(@Param("place")long place,@Param("user")long user,@Param("content")String content,@Param("parent")Long parent,@Param("root")Long root,@Param("bytes")byte[] bytes,@Param("mime")String mime);
 @Insert("INSERT INTO user_notification(user_id,kind,title,link) VALUES(#{user},'REPLY',#{title},#{link})") void notifyReply(@Param("user")long user,@Param("title")String title,@Param("link")String link);
 @Select("SELECT LAST_INSERT_ID()") long last();
 record Media(byte[] data,String mime){}
 @Select("SELECT media AS data,media_type AS mime FROM place_comment WHERE id=#{id}") Media media(long id);
 record Avatar(byte[] data){}
 @Select("SELECT avatar AS data FROM app_user WHERE id=#{id}") Avatar avatar(long id);
}
