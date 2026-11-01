package cn.edu.sdu.smartlife;

import jakarta.servlet.http.HttpServletRequest;
import java.security.Principal;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@RestController
public class RealtimeController {
 private final RealtimeHub hub;
 private final UserMapper users;
 public RealtimeController(RealtimeHub hub,UserMapper users){this.hub=hub;this.users=users;}
 @GetMapping(value="/api/events",produces=MediaType.TEXT_EVENT_STREAM_VALUE)
 public ResponseEntity<SseEmitter> events(Principal principal,HttpServletRequest request){
  return ResponseEntity.ok().header("Cache-Control","no-store").header("X-Accel-Buffering","no")
   .body(hub.subscribe(CurrentUser.id(principal),request.getSession(false)));
 }
}
