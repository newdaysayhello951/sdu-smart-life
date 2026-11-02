package cn.edu.sdu.smartlife;

import java.nio.file.*;
import java.time.Duration;
import java.util.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.ai.openai.*;
import org.springframework.ai.openai.api.OpenAiApi;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.web.client.RestClient;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.netty.http.client.HttpClient;

/** Only model settings are read from the explicitly selected local env file. */
@Component
public class CampusAiConfig {
 public final boolean enabled;
 public final Path modelDir;
 public final String qdrantUrl;
 public final String collection;
 private final String key,base,model;
 private volatile OpenAiChatModel chat;
 public CampusAiConfig(@Value("${campus.ai.enabled:false}") boolean enabled,
   @Value("${campus.ai.env-file:.env.ai}") String envFile,
   @Value("${campus.ai.model-dir:.tools/ai}") String modelDir,
   @Value("${campus.ai.qdrant-url:http://127.0.0.1:6333}") String qdrantUrl,
   @Value("${campus.ai.collection:campus_sdu_e5_v1}") String collection) throws java.io.IOException {
  this.enabled=enabled;this.modelDir=Path.of(modelDir);this.qdrantUrl=qdrantUrl;this.collection=collection;
  if(!collection.matches("[a-zA-Z0-9_]{1,80}"))throw new IllegalArgumentException("Invalid AI collection");
  Map<String,String> values=new HashMap<>();
  if(Files.exists(Path.of(envFile)))for(String line:Files.readAllLines(Path.of(envFile))){
   if(line.stripLeading().startsWith("#")||!line.contains("="))continue;
   int at=line.indexOf('=');String name=line.substring(0,at).strip(),value=line.substring(at+1).strip();
   if(!Set.of("LLM_API_KEY","DEEPSEEK_API_KEY","LLM_BASE_URL","LLM_MODEL").contains(name))continue;
   if(value.length()>1&&((value.startsWith("\"")&&value.endsWith("\""))||(value.startsWith("'")&&value.endsWith("'"))))value=value.substring(1,value.length()-1);
   values.put(name,value);
  }
  for(String name:List.of("LLM_API_KEY","DEEPSEEK_API_KEY","LLM_BASE_URL","LLM_MODEL"))if(System.getenv(name)!=null)values.put(name,System.getenv(name));
  key=values.getOrDefault("LLM_API_KEY", "").isBlank()?values.getOrDefault("DEEPSEEK_API_KEY", ""):values.get("LLM_API_KEY");
  base=values.getOrDefault("LLM_BASE_URL","https://api.deepseek.com").replaceAll("/chat/completions/?$","").replaceAll("/+$","");
  model=values.getOrDefault("LLM_MODEL","deepseek-flash");
 }
 public boolean configured(){return enabled&&!key.isBlank();}
 public synchronized OpenAiChatModel chat(){
  if(!configured())throw new IllegalStateException("校园助手尚未配置模型");
  if(chat==null){
   var factory=new JdkClientHttpRequestFactory(java.net.http.HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).build());factory.setReadTimeout(Duration.ofSeconds(55));
   var web=WebClient.builder().clientConnector(new org.springframework.http.client.reactive.ReactorClientHttpConnector(HttpClient.create().responseTimeout(Duration.ofSeconds(55))));
   var api=OpenAiApi.builder().baseUrl(base).completionsPath("/chat/completions").apiKey(key).restClientBuilder(RestClient.builder().requestFactory(factory)).webClientBuilder(web).build();
   chat=OpenAiChatModel.builder().openAiApi(api).retryTemplate(org.springframework.retry.support.RetryTemplate.builder().maxAttempts(1).fixedBackoff(1).build())
    .defaultOptions(OpenAiChatOptions.builder().model(model).temperature(0.2).maxTokens(1600).internalToolExecutionEnabled(false).build()).build();
  }
  return chat;
 }
}
