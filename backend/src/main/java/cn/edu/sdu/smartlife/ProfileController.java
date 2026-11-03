package cn.edu.sdu.smartlife;
import java.security.Principal;
import java.io.*;
import java.util.Map;
import javax.imageio.ImageIO;
import jakarta.servlet.http.*;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import org.apache.ibatis.annotations.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.http.*;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.web.context.HttpSessionSecurityContextRepository;
@RestController
@RequestMapping("/api/profile")
public class ProfileController {
 private final ProfileMapper profiles;
 public ProfileController(ProfileMapper profiles){this.profiles=profiles;}
 public record Profile(String username,String signature,String location,String qq,String dormitory){}
 public record Input(@NotBlank @Pattern(regexp="[a-zA-Z0-9_-]{3,32}") String username,@NotNull @Size(max=300) String signature,@NotNull @Size(max=120) String location,@NotNull @Pattern(regexp="[0-9]{0,20}") String qq,@NotNull @Size(max=120) String dormitory){}
 @GetMapping public Profile get(Principal p){return profiles.find(CurrentUser.id(p));}
 @PutMapping public Profile save(@Valid @RequestBody Input input,Principal p,HttpServletRequest request,HttpServletResponse response){
  try{profiles.save(CurrentUser.id(p),input);}catch(DuplicateKeyException e){throw new ResponseStatusException(HttpStatus.CONFLICT,"用户名已存在");}
  var old=SecurityContextHolder.getContext().getAuthentication();var authentication=UsernamePasswordAuthenticationToken.authenticated(input.username(),null,java.util.List.of());authentication.setDetails(old.getDetails());var context=SecurityContextHolder.createEmptyContext();context.setAuthentication(authentication);SecurityContextHolder.setContext(context);new HttpSessionSecurityContextRepository().saveContext(context,request,response);
  return profiles.find(CurrentUser.id(p));
 }
 @PostMapping("/avatar") public void avatar(@RequestParam("file") MultipartFile file,Principal p) throws IOException {
  if(file.isEmpty()||file.getSize()>5*1024*1024)throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
  java.awt.image.BufferedImage image;
  try(var in=ImageIO.createImageInputStream(file.getInputStream())){var readers=ImageIO.getImageReaders(in);if(!readers.hasNext())throw new ResponseStatusException(HttpStatus.BAD_REQUEST);var reader=readers.next();try{reader.setInput(in);var format=reader.getFormatName();if((!format.equalsIgnoreCase("png")&&!format.equalsIgnoreCase("jpeg"))||(long)reader.getWidth(0)*reader.getHeight(0)>16000000)throw new ResponseStatusException(HttpStatus.BAD_REQUEST);image=reader.read(0);}finally{reader.dispose();}}
  catch(javax.imageio.IIOException e){throw new ResponseStatusException(HttpStatus.BAD_REQUEST);}
  var out=new ByteArrayOutputStream();ImageIO.write(image,"png",out);if(out.size()>16*1024*1024)throw new ResponseStatusException(HttpStatus.BAD_REQUEST);profiles.avatar(CurrentUser.id(p),out.toByteArray());
 }
 @GetMapping("/avatar") public ResponseEntity<byte[]> avatar(Principal p,@RequestParam(defaultValue="0") int w) throws IOException {var stored=profiles.avatarData(CurrentUser.id(p));byte[] data=stored==null?null:stored.data();if(data==null){try(var in=getClass().getResourceAsStream("/default-avatar.jpg")){data=in.readAllBytes();}return ImagePreview.response(data,"image/jpeg",w);}return ImagePreview.response(data,"image/png",w);}
}
@Mapper
interface ProfileMapper {
 @Select("SELECT username,signature,location,qq,dormitory FROM app_user WHERE id=#{id}") ProfileController.Profile find(long id);
 @Update("UPDATE app_user SET username=#{input.username},signature=#{input.signature},location=#{input.location},qq=#{input.qq},dormitory=#{input.dormitory} WHERE id=#{id}") void save(@Param("id") long id,@Param("input") ProfileController.Input input);
 @Update("UPDATE app_user SET avatar=#{data} WHERE id=#{id}") void avatar(@Param("id") long id,@Param("data") byte[] data);
 record Avatar(byte[] data){}
 @Select("SELECT avatar AS data FROM app_user WHERE id=#{id}") Avatar avatarData(long id);
}
