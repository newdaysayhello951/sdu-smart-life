package cn.edu.sdu.smartlife;
import java.security.Principal;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import org.apache.ibatis.annotations.*;
import org.springframework.web.bind.annotation.*;
@RestController
@RequestMapping("/api/profile")
public class ProfileController {
 private final ProfileMapper profiles;
 public ProfileController(ProfileMapper profiles){this.profiles=profiles;}
 public record Profile(String username,String displayName,String signature,String location){}
 public record Input(@NotNull @Size(max=50) String displayName,@NotNull @Size(max=300) String signature,@NotNull @Size(max=120) String location){}
 @GetMapping public Profile get(Principal p){return profiles.find(p.getName());}
 @PutMapping public Profile save(@Valid @RequestBody Input input,Principal p){profiles.save(p.getName(),input);return get(p);}
}
@Mapper
interface ProfileMapper {
 @Select("SELECT username,display_name AS displayName,signature,location FROM app_user WHERE username=#{name}") ProfileController.Profile find(String name);
 @Update("UPDATE app_user SET display_name=#{input.displayName},signature=#{input.signature},location=#{input.location} WHERE username=#{name}") void save(@Param("name") String name,@Param("input") ProfileController.Input input);
}
