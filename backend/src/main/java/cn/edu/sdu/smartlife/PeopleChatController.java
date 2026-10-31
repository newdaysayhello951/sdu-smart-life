package cn.edu.sdu.smartlife;
import java.security.Principal;
import java.util.*;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import org.apache.ibatis.annotations.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;
@RestController
public class PeopleChatController {
 private final PeopleChatMapper db;private final UserMapper users;
 public PeopleChatController(PeopleChatMapper db,UserMapper users){this.db=db;this.users=users;}
 public record Person(long id,String username,String signature,String location,String qq,String dormitory){}
 public record Chat(long id,long peerId,String peerName,long unread){}
 public record Message(long id,long senderId,String username,String content,String createdAt){}
 public record Notification(long id,String kind,String title,String link,boolean unread,String createdAt){}
 public record Input(@NotBlank @Size(max=2000) String content){}
 private long me(Principal p){return users.find(p.getName()).id();}
 @GetMapping("/api/people/{id}") public Person person(@PathVariable long id){var person=db.person(id);if(person==null)throw new ResponseStatusException(HttpStatus.NOT_FOUND);return person;}
 @GetMapping("/api/people/me") public Person self(Principal p){return person(me(p));}
 @GetMapping("/api/people/{id}/listings") public List<ProductMapper.Product> listings(@PathVariable long id,@RequestParam(defaultValue="SELL") String kind,@RequestParam(defaultValue="0") long before){person(id);if(before<0||!List.of("SELL","WANTED").contains(kind))throw new ResponseStatusException(HttpStatus.BAD_REQUEST);return db.listings(id,kind,before);}
 @PostMapping("/api/chats/with/{peer}") @org.springframework.transaction.annotation.Transactional public Map<String,Long> open(@PathVariable long peer,Principal p){long self=me(p);if(peer==self)throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"不能私聊自己");person(peer);long low=Math.min(self,peer),high=Math.max(self,peer);db.open(low,high);return Map.of("id",db.chatId(low,high));}
 @GetMapping("/api/chats") public List<Chat> chats(Principal p){return db.chats(me(p));}
 private void require(long id,long user){if(db.member(id,user)==0)throw new ResponseStatusException(HttpStatus.NOT_FOUND);}
 @GetMapping("/api/chats/{id}/messages") public List<Message> messages(@PathVariable long id,Principal p,@RequestParam(defaultValue="0") long after){if(after<0)throw new ResponseStatusException(HttpStatus.BAD_REQUEST);require(id,me(p));return db.messages(id,after);}
 @PostMapping("/api/chats/{id}/messages") @ResponseStatus(HttpStatus.CREATED) @org.springframework.transaction.annotation.Transactional public void send(@PathVariable long id,@Valid @RequestBody Input input,Principal p){long self=me(p);require(id,self);db.send(id,self,input.content().trim());long message=db.last();long peer=db.peer(id,self);db.notify(peer,self,"收到新私信","/messages/"+id,id,message);}
 @PostMapping("/api/chats/{id}/read") public void readChat(@PathVariable long id,@RequestParam long through,Principal p){if(through<0)throw new ResponseStatusException(HttpStatus.BAD_REQUEST);long self=me(p);require(id,self);db.readChat(id,self,through);}
 @GetMapping("/api/notifications") public List<Notification> notifications(Principal p,@RequestParam(defaultValue="0") long before){if(before<0)throw new ResponseStatusException(HttpStatus.BAD_REQUEST);return db.notifications(me(p),before);}
 @GetMapping("/api/notifications/unread") public Map<String,Long> unread(Principal p){return Map.of("count",db.unread(me(p)));}
 @PostMapping("/api/notifications/read-all") public void readAll(Principal p,@RequestParam long through){if(through<0)throw new ResponseStatusException(HttpStatus.BAD_REQUEST);db.readAll(me(p),through);}
 @PostMapping("/api/notifications/{id}/read") public void readOne(@PathVariable long id,Principal p){long self=me(p);if(db.ownsNotification(id,self)==0)throw new ResponseStatusException(HttpStatus.NOT_FOUND);db.readOne(id,self);}
}
@Mapper
interface PeopleChatMapper {
 @Select("SELECT id,username,signature,location,qq,dormitory FROM app_user WHERE id=#{id}") PeopleChatController.Person person(long id);
 @Select("SELECT id,title,description,price,location,image_url AS imageUrl,status,owner_id AS ownerId,(SELECT username FROM app_user WHERE id=owner_id) AS ownerName,listing_type AS kind FROM product WHERE owner_id=#{id} AND status='AVAILABLE' AND listing_type=#{kind} AND (#{before}=0 OR id<#{before}) ORDER BY id DESC LIMIT 12") List<ProductMapper.Product> listings(@Param("id")long id,@Param("kind")String kind,@Param("before")long before);
 @Insert("INSERT INTO private_chat(user_low,user_high) VALUES(#{low},#{high}) ON DUPLICATE KEY UPDATE id=id") void open(@Param("low")long low,@Param("high")long high);
 @Select("SELECT id FROM private_chat WHERE user_low=#{low} AND user_high=#{high} FOR UPDATE") long chatId(@Param("low")long low,@Param("high")long high);
 @Select("SELECT c.id,CASE WHEN c.user_low=#{user} THEN c.user_high ELSE c.user_low END AS peerId,u.username AS peerName,(SELECT COUNT(*) FROM user_notification n WHERE n.user_id=#{user} AND n.chat_id=c.id AND n.read_at IS NULL) AS unread FROM private_chat c JOIN app_user u ON u.id=CASE WHEN c.user_low=#{user} THEN c.user_high ELSE c.user_low END WHERE c.user_low=#{user} OR c.user_high=#{user} ORDER BY c.id DESC") List<PeopleChatController.Chat> chats(long user);
 @Select("SELECT COUNT(*) FROM private_chat WHERE id=#{id} AND (user_low=#{user} OR user_high=#{user})") int member(@Param("id")long id,@Param("user")long user);
 @Select("SELECT CASE WHEN user_low=#{user} THEN user_high ELSE user_low END FROM private_chat WHERE id=#{id}") long peer(@Param("id")long id,@Param("user")long user);
 @Select("SELECT m.id,m.sender_id AS senderId,u.username,m.content,CAST(m.created_at AS CHAR) AS createdAt FROM private_message m JOIN app_user u ON u.id=m.sender_id WHERE m.chat_id=#{id} AND m.id>#{after} ORDER BY m.id ASC LIMIT 50") List<PeopleChatController.Message> messages(@Param("id")long id,@Param("after")long after);
 @Insert("INSERT INTO private_message(chat_id,sender_id,content) VALUES(#{id},#{user},#{content})") void send(@Param("id")long id,@Param("user")long user,@Param("content")String content);
 @Select("SELECT LAST_INSERT_ID()") long last();
 @Insert("INSERT INTO user_notification(user_id,actor_id,kind,title,link,chat_id,message_id) VALUES(#{user},#{actor},'CHAT',#{title},#{link},#{chat},#{message})") void notify(@Param("user")long user,@Param("actor")long actor,@Param("title")String title,@Param("link")String link,@Param("chat")long chat,@Param("message")long message);
 @Select("SELECT n.id,n.kind,CASE WHEN n.kind='CHAT' AND u.id IS NOT NULL THEN CONCAT(CONVERT(u.username USING utf8mb4),' 发来私信') ELSE n.title END AS title,n.link,(n.read_at IS NULL) AS unread,CAST(n.created_at AS CHAR) AS createdAt FROM user_notification n LEFT JOIN app_user u ON u.id=n.actor_id WHERE n.user_id=#{user} AND (#{before}=0 OR n.id<#{before}) ORDER BY n.id DESC LIMIT 30") List<PeopleChatController.Notification> notifications(@Param("user")long user,@Param("before")long before);
 @Select("SELECT COUNT(*) FROM user_notification WHERE user_id=#{user} AND read_at IS NULL") long unread(long user);
 @Update("UPDATE user_notification SET read_at=CURRENT_TIMESTAMP WHERE user_id=#{user} AND id<=#{through} AND read_at IS NULL") void readAll(@Param("user")long user,@Param("through")long through);
 @Select("SELECT COUNT(*) FROM user_notification WHERE id=#{id} AND user_id=#{user}") int ownsNotification(@Param("id")long id,@Param("user")long user);
 @Update("UPDATE user_notification SET read_at=CURRENT_TIMESTAMP WHERE id=#{id} AND user_id=#{user} AND read_at IS NULL") void readOne(@Param("id")long id,@Param("user")long user);
 @Update("UPDATE user_notification SET read_at=CURRENT_TIMESTAMP WHERE chat_id=#{chat} AND user_id=#{user} AND message_id<=#{through} AND read_at IS NULL") void readChat(@Param("chat")long chat,@Param("user")long user,@Param("through")long through);
}
