package cn.edu.sdu.smartlife;

import java.util.Set;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.context.HttpSessionSecurityContextRepository;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.transaction.TransactionDefinition;
import org.springframework.transaction.event.TransactionalEventListenerFactory;
import org.springframework.transaction.support.AbstractPlatformTransactionManager;
import org.springframework.transaction.support.DefaultTransactionStatus;
import org.springframework.transaction.support.TransactionTemplate;

class RealtimeHubTest {
 private final AbstractPlatformTransactionManager manager=new AbstractPlatformTransactionManager(){
  protected Object doGetTransaction(){return new Object();}
  protected void doBegin(Object transaction,TransactionDefinition definition){}
  protected void doCommit(DefaultTransactionStatus status){}
  protected void doRollback(DefaultTransactionStatus status){}
 };
 @Test void publishesOnlyAfterCommitAndDropsRollbacks(){
  try(var context=new AnnotationConfigApplicationContext()){
   context.registerBean(TransactionalEventListenerFactory.class,TransactionalEventListenerFactory::new);
   context.registerBean(RealtimeHub.class,()->spy(new RealtimeHub(context)));context.refresh();
   var hub=context.getBean(RealtimeHub.class);var tx=new TransactionTemplate(manager);
   tx.executeWithoutResult(status->{hub.changed(7,"chat",8L);verify(hub,never()).deliver(any());});
   verify(hub).deliver(new RealtimeHub.Change(7,"chat",8L));clearInvocations(hub);
   tx.executeWithoutResult(status->{hub.changed(7,"chat",9L);status.setRollbackOnly();});
   verify(hub,never()).deliver(any());
  }
 }
 @Test void rejectsMismatchedSessionsAndDisconnectsLogout(){
  var hub=new RealtimeHub(event->{});var session=new MockHttpSession();
  var context=SecurityContextHolder.createEmptyContext();var auth=UsernamePasswordAuthenticationToken.authenticated("test",null,java.util.List.of());auth.setDetails(7L);context.setAuthentication(auth);
  session.setAttribute(HttpSessionSecurityContextRepository.SPRING_SECURITY_CONTEXT_KEY,context);
  hub.subscribe(8,session);assertEquals(0,connections(hub));
  hub.subscribe(7,session);assertEquals(1,connections(hub));
  hub.disconnect(session);assertEquals(0,connections(hub));
  hub.subscribe(7,session);session.invalidate();hub.heartbeat();assertEquals(0,connections(hub));
 }
 private int connections(RealtimeHub hub){return ((Set<?>)ReflectionTestUtils.getField(hub,"connections")).size();}
 @Test void aBrokenSocketDoesNotInterruptOtherListenersOrHeartbeat() throws Exception {
  var hub=spy(new RealtimeHub(event->{}));var broken=mock(org.springframework.web.servlet.mvc.method.annotation.SseEmitter.class);
  var healthy=mock(org.springframework.web.servlet.mvc.method.annotation.SseEmitter.class);
  doReturn(broken,healthy).when(hub).createEmitter();
  var session=new MockHttpSession();var context=SecurityContextHolder.createEmptyContext();
  var auth=UsernamePasswordAuthenticationToken.authenticated("socket-test",null,java.util.List.of());auth.setDetails(7L);context.setAuthentication(auth);
  session.setAttribute(HttpSessionSecurityContextRepository.SPRING_SECURITY_CONTEXT_KEY,context);
  hub.subscribe(7,session);hub.subscribe(7,session);
  doThrow(new java.io.IOException("disconnected")).when(broken).send(any(org.springframework.web.servlet.mvc.method.annotation.SseEmitter.SseEventBuilder.class));
  assertDoesNotThrow(()->hub.deliver(new RealtimeHub.Change(7,"chat",8L)));assertEquals(1,connections(hub));
  verify(broken,never()).complete();assertDoesNotThrow(hub::heartbeat);
  doThrow(new IllegalStateException("container already completed")).when(healthy).complete();
  assertDoesNotThrow(()->hub.disconnect(session));assertEquals(0,connections(hub));
 }
}
