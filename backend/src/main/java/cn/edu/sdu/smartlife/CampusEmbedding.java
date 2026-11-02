package cn.edu.sdu.smartlife;

import ai.onnxruntime.*;
import ai.djl.huggingface.tokenizers.HuggingFaceTokenizer;
import java.util.*;
import org.springframework.stereotype.Component;
import jakarta.annotation.PreDestroy;

/** Independent multilingual E5 ONNX model. No remote inference or other app service. */
@Component
public class CampusEmbedding {
 private final CampusAiConfig config;
 private OrtSession session;private HuggingFaceTokenizer tokenizer;
 private OrtEnvironment env;
 public CampusEmbedding(CampusAiConfig config){this.config=config;}
 private synchronized void init() throws Exception {
  if(session!=null)return;
  env=OrtEnvironment.getEnvironment();
  tokenizer=HuggingFaceTokenizer.newInstance(config.modelDir.resolve("tokenizer.json"),Map.of("maxLength","512","truncation","true","padding","false"));
  try(var options=new OrtSession.SessionOptions()){options.setIntraOpNumThreads(2);options.setInterOpNumThreads(1);session=env.createSession(config.modelDir.resolve("model.onnx").toString(),options);}
 }
 public synchronized float[] embed(String text,boolean query){
  try{init();var e=tokenizer.encode((query?"query: ":"passage: ")+text.substring(0,Math.min(text.length(),6000)));
   long[] ids=e.getIds(),mask=e.getAttentionMask(),types=e.getTypeIds();
   Map<String,OnnxTensor> inputs=new HashMap<>();
   try{
    inputs.put("input_ids",OnnxTensor.createTensor(env,new long[][]{ids}));
    inputs.put("attention_mask",OnnxTensor.createTensor(env,new long[][]{mask}));
    if(session.getInputNames().contains("token_type_ids"))inputs.put("token_type_ids",OnnxTensor.createTensor(env,new long[][]{types}));
    try(var result=session.run(inputs)){
     float[][][] hidden=(float[][][])result.get(0).getValue();float[] out=new float[hidden[0][0].length];int count=0;
     for(int i=0;i<ids.length;i++)if(mask[i]!=0){count++;for(int j=0;j<out.length;j++)out[j]+=hidden[0][i][j];}
     double norm=0;for(int j=0;j<out.length;j++){out[j]/=Math.max(1,count);norm+=out[j]*out[j];}
     norm=Math.sqrt(norm);for(int j=0;j<out.length;j++)out[j]/=(float)Math.max(norm,1e-12);return out;
    }
   }finally{inputs.values().forEach(OnnxTensor::close);}
  }catch(Exception | LinkageError e){throw new IllegalStateException("校园知识向量模型不可用，请检查独立模型安装",e);}
 }
 @PreDestroy public synchronized void close() throws Exception {if(session!=null)session.close();if(tokenizer!=null)tokenizer.close();}
}
