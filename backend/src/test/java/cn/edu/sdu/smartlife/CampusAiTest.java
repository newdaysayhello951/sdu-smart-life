package cn.edu.sdu.smartlife;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import java.util.*;

class CampusAiTest {
 @Test void sourceAllowlistRejectsUserInfoPortsAndLookalikeHosts(){
  assertNotNull(CampusKnowledge.allowed("https://nc.sdu.edu.cn/info/1.htm"));
  for(String s:List.of("http://nc.sdu.edu.cn/a","https://sdu.edu.cn.evil.org/a","https://127.0.0.1/a","https://x@nc.sdu.edu.cn/a","https://nc.sdu.edu.cn:8800/a"))assertThrows(IllegalArgumentException.class,()->CampusKnowledge.allowed(s));
 }
 @Test void overlappingChunksPreserveOriginalAndTermsSupportChinese(){
  var text="山大校园".repeat(800);var chunks=CampusKnowledge.split(text);
  assertEquals(text.substring(620,800),chunks.get(1).substring(0,180));
  assertTrue(chunks.stream().allMatch(s->s.length()<=800));
  assertTrue(CampusKnowledge.terms("校园网 WiFi").containsAll(List.of("校园","园网","wifi")));
 }
 @Test void privateToolUsesCapturedIdentityAndRequiresNotificationIntent(){
  var people=mock(PeopleChatMapper.class);when(people.unread(42)).thenReturn(3L);when(people.notifications(42,0)).thenReturn(List.of());
  var a=new CampusAssistant(mock(CampusAiConfig.class),mock(CampusKnowledge.class),mock(JdbcTemplate.class),new ObjectMapper(),mock(ProductService.class),mock(CampusMapper.class),people);
  var tools=a.new RequestTools(42,(name,data)->{},()->true,"查询我的未读通知");
  assertTrue(tools.myCampusNotifications().contains("3"));verify(people).unread(42);verify(people).notifications(42,0);
  reset(people);var noIntent=a.new RequestTools(42,(name,data)->{},()->true,"图书馆怎么借书");assertTrue(noIntent.myCampusNotifications().contains("不能读取"));verifyNoInteractions(people);
  var expired=a.new RequestTools(42,(name,data)->{},()->false,"我的通知");assertThrows(IllegalStateException.class,expired::myCampusNotifications);verifyNoInteractions(people);
 }
}
