package cn.edu.sdu.smartlife;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.web.server.ResponseStatusException;
class CurrentUserTest {
 @Test void identityDoesNotDependOnEditableUsername(){
  var old=UsernamePasswordAuthenticationToken.authenticated("before",null,java.util.List.of());old.setDetails(9L);
  var renamed=UsernamePasswordAuthenticationToken.authenticated("after",null,java.util.List.of());renamed.setDetails(9L);
  assertEquals(CurrentUser.id(old),CurrentUser.id(renamed));
  assertThrows(ResponseStatusException.class,()->CurrentUser.id(()->"forged-name"));
 }
}
