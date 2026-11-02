package cn.edu.sdu.smartlife;

import com.fasterxml.jackson.databind.*;
import java.net.*;
import java.net.http.*;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;
import org.jsoup.Jsoup;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.support.TransactionTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.scheduling.annotation.Scheduled;

@Service
public class CampusKnowledge {
 public record Seed(String url,String title,String campus){}
 public record Hit(String id,String title,String url,String campus,String fetchedAt,String content,double score){}
 private record Chunk(String id,String title,String url,String campus,String fetched,String content,float[] vector){}
 private final JdbcTemplate db;private final ObjectMapper json;private final CampusEmbedding embedding;private final CampusAiConfig config;private final TransactionTemplate tx;
 private final HttpClient http=HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).followRedirects(HttpClient.Redirect.NEVER).build();
 private final AtomicBoolean ingesting=new AtomicBoolean();
 private volatile String syncStatus="尚未采集";private volatile String retrievalMode="尚未检索";
 private final boolean ingestOnStart;
 public CampusKnowledge(JdbcTemplate db,ObjectMapper json,CampusEmbedding embedding,CampusAiConfig config,org.springframework.transaction.PlatformTransactionManager tm,@Value("${campus.ai.ingest-on-start:true}")boolean ingestOnStart){this.db=db;this.json=json;this.embedding=embedding;this.config=config;this.tx=new TransactionTemplate(tm);this.ingestOnStart=ingestOnStart;}
 @Value("${campus.ai.import-only:false}") private boolean importOnly;
 @EventListener(ApplicationReadyEvent.class) public void start(){if(config.enabled&&ingestOnStart)Thread.ofVirtual().name("campus-knowledge-import").start(()->{refresh();if(importOnly)System.exit(0);});}
 @Scheduled(fixedDelayString="${campus.ai.refresh-ms:86400000}",initialDelayString="${campus.ai.refresh-ms:86400000}")public void scheduled(){if(config.enabled)refresh();}
 public Map<String,Object> status(){return Map.of("documents",db.queryForObject("SELECT COUNT(*) FROM ai_knowledge_source",Long.class),"chunks",db.queryForObject("SELECT COUNT(*) FROM ai_knowledge_chunk",Long.class),"sync",syncStatus,"retrieval",retrievalMode,"syncing",ingesting.get());}
 public synchronized void refresh(){
  if(!ingesting.compareAndSet(false,true))return;
  int ok=0,failed=0;
  try(var in=getClass().getResourceAsStream("/campus-knowledge-sources.json")){
   Seed[] seeds=json.readValue(in,Seed[].class);
   for(var seed:seeds){try{ingest(seed);ok++;}catch(Exception e){failed++;org.slf4j.LoggerFactory.getLogger(CampusKnowledge.class).warn("Campus source failed: "+seed.title(),e);}try{Thread.sleep(350);}catch(InterruptedException e){Thread.currentThread().interrupt();break;}}
   syncStatus="采集完成："+ok+" 个来源成功，"+failed+" 个失败（保留已有版本）";
   try{rebuildIndex();}catch(Exception e){syncStatus+="；向量索引同步失败，仍可从 MySQL 向量检索";}
  }catch(Exception e){syncStatus="采集失败，保留已入库资料";}finally{ingesting.set(false);}
 }
 static URI allowed(String url){
  URI uri=URI.create(url);String host=uri.getHost();
  if(!"https".equals(uri.getScheme())||host==null||!host.endsWith(".sdu.edu.cn")||uri.getUserInfo()!=null||(uri.getPort()!=-1&&uri.getPort()!=443))throw new IllegalArgumentException("仅允许山东大学官方HTTPS资料");
  return uri;
 }
 private void ingest(Seed seed)throws Exception{
  URI uri=allowed(seed.url());
  var req=HttpRequest.newBuilder(uri).timeout(Duration.ofSeconds(18)).header("User-Agent","SmartCampusKnowledge/1.0 (public campus guidance; low-rate)").GET().build();
  var response=http.send(req,HttpResponse.BodyHandlers.ofInputStream());
  byte[] bytes;try(var in=response.body()){if(response.statusCode()!=200)throw new IllegalStateException("Source unavailable");bytes=in.readNBytes(50_000_001);}
  if(bytes.length>50_000_000)throw new IllegalStateException("Source too large");
  String text;
  if(response.headers().firstValue("Content-Type").orElse("").contains("pdf")||uri.getPath().endsWith(".pdf")){
   try(var pdf=org.apache.pdfbox.Loader.loadPDF(bytes)){var stripper=new org.apache.pdfbox.text.PDFTextStripper();stripper.setEndPage(Math.min(60,pdf.getNumberOfPages()));text=stripper.getText(pdf);}
  }else{
   var doc=Jsoup.parse(new java.io.ByteArrayInputStream(bytes),null,seed.url());
   doc.select("script,style,nav,header,footer,.nav,.header,.footer,.sidebar").remove();
   var content=doc.select("#vsb_content,[id^=vsb_content],.art-body,.v_news_content,.article-content,.article_content,.news_content,.read-content").stream().max(Comparator.comparingInt(e->e.text().length())).orElse(null);
   if(content==null)content=doc.select("main,#content,.content").stream().max(Comparator.comparingInt(e->e.text().length())).orElse(doc.body());
   content.select("td,th").forEach(cell->cell.appendText(" | "));
   text=content.wholeText();
   // Directory links remain useful as explicit entry points, not invented instructions.
   var links=content.select("a[href]");StringBuilder linked=new StringBuilder();
   for(var a:links){String href=a.absUrl("href");if(href.startsWith("https://")&&href.contains(".sdu.edu.cn")&&!a.text().isBlank())linked.append("\n").append(a.text()).append("：").append(href);}
   text+=linked;
  }
  text=text.replaceAll("[\\t\\x0B\\f\\r ]+"," ").replaceAll("\\n{3,}","\n\n").strip();
  if(text.length()<80)throw new IllegalStateException("No useful text");if(text.length()>100000)text=text.substring(0,100000);
  String hash=HexFormat.of().formatHex(java.security.MessageDigest.getInstance("SHA-256").digest(text.getBytes(java.nio.charset.StandardCharsets.UTF_8)));
  var old=db.queryForList("SELECT id,content_hash FROM ai_knowledge_source WHERE url=?",seed.url());
  if(!old.isEmpty()&&hash.equals(old.get(0).get("content_hash"))){db.update("UPDATE ai_knowledge_source SET title=?,campus=?,fetched_at=CURRENT_TIMESTAMP WHERE url=?",seed.title(),seed.campus(),seed.url());return;}
  var pieces=split(text);List<float[]> vectors=new ArrayList<>();
  for(String piece:pieces)vectors.add(embedding.embed(seed.title()+" "+piece,false));
  String body=text;
  tx.executeWithoutResult(s->{
   db.update("INSERT INTO ai_knowledge_source(url,title,campus,content,content_hash) VALUES(?,?,?,?,?) ON DUPLICATE KEY UPDATE title=VALUES(title),campus=VALUES(campus),content=VALUES(content),content_hash=VALUES(content_hash),fetched_at=CURRENT_TIMESTAMP",seed.url(),seed.title(),seed.campus(),body,hash);
   long id=db.queryForObject("SELECT id FROM ai_knowledge_source WHERE url=?",Long.class,seed.url());
   db.update("DELETE FROM ai_knowledge_chunk WHERE source_id=?",id);
   for(int i=0;i<pieces.size();i++)db.update("INSERT INTO ai_knowledge_chunk(id,source_id,ordinal,content,embedding) VALUES(?,?,?,?,?)",UUID.randomUUID().toString(),id,i,pieces.get(i),encode(vectors.get(i)));
  });
 }
 static List<String> split(String text){List<String> out=new ArrayList<>();for(int start=0;start<text.length();start+=620){out.add(text.substring(start,Math.min(start+800,text.length())));if(start+800>=text.length())break;}return out;}
 private String encode(Object value){try{return json.writeValueAsString(value);}catch(Exception e){throw new IllegalStateException(e);}}
 private List<Chunk> chunks(){return db.query("SELECT c.id,s.title,s.url,s.campus,CAST(s.fetched_at AS CHAR),c.content,c.embedding FROM ai_knowledge_chunk c JOIN ai_knowledge_source s ON s.id=c.source_id ORDER BY c.source_id,c.ordinal LIMIT 10000",(r,i)->{try{return new Chunk(r.getString(1),r.getString(2),r.getString(3),r.getString(4),r.getString(5),r.getString(6),json.readValue(r.getString(7),float[].class));}catch(Exception e){throw new IllegalStateException(e);}});}
 private JsonNode qdrant(String method,String suffix,Object body)throws Exception{
  var b=HttpRequest.newBuilder(URI.create(config.qdrantUrl+"/collections/"+config.collection+suffix)).timeout(Duration.ofSeconds(8)).header("Content-Type","application/json");
  var result=http.send(b.method(method,body==null?HttpRequest.BodyPublishers.noBody():HttpRequest.BodyPublishers.ofString(encode(body))).build(),HttpResponse.BodyHandlers.ofString());
  if(result.statusCode()<200||result.statusCode()>299)throw new IllegalStateException("Vector index unavailable");return json.readTree(result.body());
 }
 public void rebuildIndex()throws Exception{
  try{qdrant("GET","",null);}catch(Exception e){qdrant("PUT","",Map.of("vectors",Map.of("size",384,"distance","Cosine")));}
  var all=chunks();
  qdrant("POST","/points/delete?wait=true",Map.of("filter",Map.of()));
  // MySQL is authoritative. Search resolves only IDs which still exist there.
  for(int start=0;start<all.size();start+=32){List<Object> points=new ArrayList<>();for(var c:all.subList(start,Math.min(start+32,all.size())))points.add(Map.of("id",c.id(),"vector",c.vector()));qdrant("PUT","/points?wait=true",Map.of("points",points));}
 }
 public List<Hit> search(String query){
  if(query==null||query.isBlank()||query.length()>1000)throw new IllegalArgumentException("检索词长度无效");
  var all=chunks();if(all.isEmpty())return List.of();float[] q=embedding.embed(query,true);
  Map<String,Double> scores=new HashMap<>();Map<String,Chunk> byId=new HashMap<>();for(var c:all)byId.put(c.id(),c);
  List<Chunk> dense;
  try{var hits=qdrant("POST","/points/search",Map.of("vector",q,"limit",20)).path("result");dense=new ArrayList<>();for(var h:hits){var c=byId.get(h.path("id").asText());if(c!=null)dense.add(c);}retrievalMode="Qdrant 语义 + BM25";}
  catch(Exception e){dense=all.stream().sorted(Comparator.comparingDouble((Chunk c)->cosine(q,c.vector())).reversed()).limit(20).toList();retrievalMode="MySQL 语义向量 + BM25（Qdrant不可用）";}
  for(int i=0;i<dense.size();i++)scores.merge(dense.get(i).id(),1.0/(60+i+1),Double::sum);
  var terms=terms(query);Map<String,Double> lexical=new HashMap<>();Map<String,Integer> df=new HashMap<>();
  var docs=new HashMap<String,List<String>>();double avg=0;
  for(var c:all){var ts=terms(c.title()+" "+c.content());docs.put(c.id(),ts);avg+=ts.size();for(String t:new HashSet<>(ts))df.merge(t,1,Integer::sum);}avg/=Math.max(1,all.size());
  for(var c:all){var ts=docs.get(c.id());double score=0;for(String term:new HashSet<>(terms)){long f=ts.stream().filter(term::equals).count();if(f>0){double idf=Math.log(1+(all.size()-df.getOrDefault(term,0)+.5)/(df.getOrDefault(term,0)+.5));score+=idf*(f*2.2)/(f+1.2*(.25+.75*ts.size()/Math.max(1,avg)));}}if(score>0)lexical.put(c.id(),score);}
  var lex=lexical.entrySet().stream().sorted(Map.Entry.<String,Double>comparingByValue().reversed()).limit(20).toList();for(int i=0;i<lex.size();i++)scores.merge(lex.get(i).getKey(),1.0/(60+i+1),Double::sum);
  return scores.entrySet().stream().sorted(Map.Entry.<String,Double>comparingByValue().reversed()).limit(6).map(e->{var c=byId.get(e.getKey());return new Hit(c.id(),c.title(),c.url(),c.campus(),c.fetched(),c.content(),e.getValue());}).toList();
 }
 static double cosine(float[] a,float[] b){if(a.length!=b.length)return -1;double n=0;for(int i=0;i<a.length;i++)n+=a[i]*b[i];return n;}
 static List<String> terms(String text){var result=new ArrayList<String>();String s=text.toLowerCase(Locale.ROOT);var m=java.util.regex.Pattern.compile("[a-z0-9]+|[\\p{IsHan}]+").matcher(s);while(m.find()){String t=m.group();if(t.charAt(0)>127){for(int i=0;i<t.length()-1;i++)result.add(t.substring(i,i+2));if(t.length()==1)result.add(t);}else result.add(t);}return result;}
}
