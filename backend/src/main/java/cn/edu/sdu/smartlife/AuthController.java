package cn.edu.sdu.smartlife;
import jakarta.servlet.http.*;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import java.util.Map;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.http.HttpStatus;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.web.context.HttpSessionSecurityContextRepository;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
@RestController
@RequestMapping("/api/auth")
public class AuthController {
 private final UserMapper users; private final BCryptPasswordEncoder encoder;
 public AuthController(UserMapper users,BCryptPasswordEncoder encoder){this.users=users;this.encoder=encoder;}
 public record Credentials(@NotBlank @Pattern(regexp="[a-zA-Z0-9_\\-]{3,32}") String username,@NotBlank @Size(min=8,max=64) String password) {}
 @GetMapping("/csrf") public Map<String,String> csrf(CsrfToken token){return Map.of("token",token.getToken());}
 @PostMapping("/register") @ResponseStatus(HttpStatus.CREATED)
 public Map<String,String> register(@Valid @RequestBody Credentials input){
  try{users.insert(new UserMapper.Account(null,input.username(),encoder.encode(input.password())));}
  catch(DuplicateKeyException e){throw new ResponseStatusException(HttpStatus.CONFLICT,"用户名已存在");}
  return Map.of("username",input.username());
 }
 @PostMapping("/login") public Map<String,String> login(@Valid @RequestBody Credentials input,HttpServletRequest request,HttpServletResponse response){
  var user=users.find(input.username());
  if(user==null || !encoder.matches(input.password(),user.passwordHash())) throw new ResponseStatusException(HttpStatus.UNAUTHORIZED,"用户名或密码错误");
  if(request.getSession(false)!=null) request.changeSessionId();
  var context=SecurityContextHolder.createEmptyContext();
  var authentication=UsernamePasswordAuthenticationToken.authenticated(user.username(),null,java.util.List.of());authentication.setDetails(user.id());context.setAuthentication(authentication);
  SecurityContextHolder.setContext(context);
  new HttpSessionSecurityContextRepository().saveContext(context,request,response);
  return Map.of("username",user.username());
 }
 @GetMapping("/me") public Map<String,String> me(){var a=SecurityContextHolder.getContext().getAuthentication();if(a==null||!a.isAuthenticated()||"anonymousUser".equals(a.getPrincipal()))throw new ResponseStatusException(HttpStatus.UNAUTHORIZED);return Map.of("username",a.getName());}
}
