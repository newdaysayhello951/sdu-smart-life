package cn.edu.sdu.smartlife;

import jakarta.annotation.PreDestroy;
import jakarta.servlet.http.HttpSession;
import java.io.IOException;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.web.context.HttpSessionSecurityContextRepository;
import org.springframework.stereotype.Component;
import org.springframework.transaction.event.TransactionPhase;
import org.springframework.transaction.event.TransactionalEventListener;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

/** Pushes invalidation hints only; content remains behind the ordinary authenticated APIs. */
@Component
public class RealtimeHub {
 public record Change(long userId,String kind,Long chatId){}
 private record Connection(long userId,HttpSession session,SseEmitter emitter){}
 private final Set<Connection> connections=ConcurrentHashMap.newKeySet();
 private final ApplicationEventPublisher events;
 public RealtimeHub(ApplicationEventPublisher events){this.events=events;}

 public SseEmitter subscribe(long userId,HttpSession session){
  var emitter=new SseEmitter(15*60*1000L);
  var connection=new Connection(userId,session,emitter);
  connections.add(connection);
  emitter.onCompletion(()->connections.remove(connection));
  emitter.onTimeout(()->close(connection));
  emitter.onError(error->connections.remove(connection));
  send(connection,"ready",Map.of("resync",true));
  return emitter;
 }
 public void changed(long userId,String kind,Long chatId){events.publishEvent(new Change(userId,kind,chatId));}
 @TransactionalEventListener(phase=TransactionPhase.AFTER_COMMIT,fallbackExecution=true)
 public void deliver(Change change){
  var data=change.chatId()==null?Map.<String,Object>of("kind",change.kind()):Map.<String,Object>of("kind",change.kind(),"chatId",change.chatId());
  connections.stream().filter(c->c.userId()==change.userId()).forEach(c->send(c,"update",data));
 }
 private boolean authorized(Connection connection){
  try{
   var context=connection.session().getAttribute(HttpSessionSecurityContextRepository.SPRING_SECURITY_CONTEXT_KEY);
   return context instanceof SecurityContext security && security.getAuthentication()!=null
    && Long.valueOf(connection.userId()).equals(security.getAuthentication().getDetails());
  }catch(IllegalStateException expired){return false;}
 }
 private void send(Connection connection,String event,Object data){
  synchronized(connection){
   if(!authorized(connection)){close(connection);return;}
   try{connection.emitter().send(SseEmitter.event().name(event).reconnectTime(3000).data(data));}
   catch(IOException|IllegalStateException disconnected){close(connection);}
  }
 }
 private void close(Connection connection){connections.remove(connection);connection.emitter().complete();}
 public void disconnect(HttpSession session){if(session!=null)connections.stream().filter(c->c.session()==session).forEach(this::close);}
 @Scheduled(fixedDelay=20000) public void heartbeat(){connections.forEach(c->send(c,"heartbeat",Map.of("alive",true)));}
 @PreDestroy public void shutdown(){connections.forEach(this::close);}
}
