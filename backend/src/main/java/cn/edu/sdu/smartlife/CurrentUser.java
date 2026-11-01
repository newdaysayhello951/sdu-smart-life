package cn.edu.sdu.smartlife;

import java.security.Principal;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;
import org.springframework.web.server.ResponseStatusException;

/** Username is editable; ownership must always come from the authenticated stable ID. */
final class CurrentUser {
 private CurrentUser(){}
 static long id(Principal principal){
  if(principal instanceof Authentication auth && auth.isAuthenticated() && auth.getDetails() instanceof Long id)return id;
  throw new ResponseStatusException(HttpStatus.UNAUTHORIZED);
 }
}
