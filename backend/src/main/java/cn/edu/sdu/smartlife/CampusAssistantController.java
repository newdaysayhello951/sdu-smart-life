package cn.edu.sdu.smartlife;

import java.security.Principal;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import jakarta.servlet.http.HttpSession;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@RestController
@RequestMapping("/api/assistant")
public class CampusAssistantController {
 private final CampusAssistant assistant;
 public CampusAssistantController(CampusAssistant assistant){this.assistant=assistant;}
 public record Ask(@NotBlank @Size(max=36) String conversationId,@NotBlank @Size(max=2000)String question){}
 @GetMapping("/status")public Map<String,Object> status(){return assistant.status();}
 @GetMapping("/conversations")public List<Map<String,Object>> list(Principal p){return assistant.conversations(CurrentUser.id(p));}
 @PostMapping("/conversations")public Map<String,String> create(Principal p){return assistant.create(CurrentUser.id(p));}
 @GetMapping("/conversations/{id}")public List<Map<String,Object>> history(@PathVariable String id,Principal p){return assistant.history(id,CurrentUser.id(p));}
 @PostMapping("/cancel") @ResponseStatus(org.springframework.http.HttpStatus.NO_CONTENT) public void cancel(Principal p){assistant.cancel(CurrentUser.id(p));}
 @PostMapping(value="/ask",produces="text/event-stream")public SseEmitter ask(@Valid @RequestBody Ask ask,Principal p,HttpSession session){
  long user=CurrentUser.id(p);assistant.require(ask.conversationId(),user);assistant.reserve(user);
  var stream=new SseEmitter(175000L);var live=new AtomicBoolean(true);
  stream.onTimeout(()->live.set(false));stream.onCompletion(()->live.set(false));stream.onError(e->live.set(false));
  java.util.function.BooleanSupplier alive=()->{if(!live.get())return false;try{session.getCreationTime();return true;}catch(IllegalStateException e){return false;}};
  Thread.ofVirtual().name("campus-assistant-"+user).start(()->{
   try{assistant.answer(ask.conversationId(),user,ask.question().trim(),(name,data)->{if(!alive.getAsBoolean())throw new IllegalStateException("连接已断开");try{stream.send(SseEmitter.event().name(name).data(data));}catch(Exception e){live.set(false);throw new IllegalStateException("连接已断开");}},alive);}
   finally{live.set(false);try{stream.complete();}catch(IllegalStateException ignored){}}
  });return stream;
 }
}
