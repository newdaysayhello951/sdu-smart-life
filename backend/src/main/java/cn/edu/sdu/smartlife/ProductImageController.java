package cn.edu.sdu.smartlife;
import java.nio.file.*;
import java.io.*;
import java.security.Principal;
import java.util.*;
import javax.imageio.ImageIO;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.*;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.server.ResponseStatusException;
@RestController
public class ProductImageController {
 private final ProductMapper products;private final UserMapper users;private final ProductImageMapper images;
 public ProductImageController(ProductMapper products,UserMapper users,ProductImageMapper images){this.products=products;this.users=users;this.images=images;}
 @org.springframework.transaction.annotation.Transactional(rollbackFor=Exception.class)
 @PostMapping("/api/my/products/{id}/image") public Map<String,String> upload(@PathVariable long id,@RequestParam("file") MultipartFile file,Principal principal) throws IOException {
  long owner=CurrentUser.id(principal);
  if(products.owned(id,owner)!=1)throw new ResponseStatusException(HttpStatus.NOT_FOUND);
  if(file.isEmpty()||file.getSize()>5*1024*1024)throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"图片应小于5MB");
  java.awt.image.BufferedImage image;
  try(var input=ImageIO.createImageInputStream(file.getInputStream())){
   var readers=ImageIO.getImageReaders(input);if(!readers.hasNext())throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"仅支持JPEG或PNG图片");
   var reader=readers.next();try{reader.setInput(input);String format=reader.getFormatName();if(!(format.equalsIgnoreCase("png")||format.equalsIgnoreCase("jpeg"))||(long)reader.getWidth(0)*reader.getHeight(0)>16000000)throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"图片格式或尺寸无效");image=reader.read(0);}finally{reader.dispose();}
  }catch(javax.imageio.IIOException e){throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"无法读取图片");}
  var output=new ByteArrayOutputStream();ImageIO.write(image,"png",output);
  if(output.size()>16*1024*1024)throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"图片解码后过大");
  String url="/api/images/product/"+id;
  if(products.image(id,owner,url)!=1)throw new ResponseStatusException(HttpStatus.CONFLICT);
  images.save(id,output.toByteArray());return Map.of("imageUrl",url);
 }
 @GetMapping("/api/images/product/{id}") public ResponseEntity<byte[]> image(@PathVariable long id,@RequestParam(defaultValue="0") int w) throws IOException {
  var image=images.find(id);if(image==null)throw new ResponseStatusException(HttpStatus.NOT_FOUND);
  if(w<0||w>1280)throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"图片尺寸无效");
  if(w>0){
   var source=ImageIO.read(new ByteArrayInputStream(image.data()));
   if(source!=null){
    double ratio=Math.min(1.0,(double)w/Math.max(source.getWidth(),source.getHeight()));
    var small=new java.awt.image.BufferedImage(Math.max(1,(int)(source.getWidth()*ratio)),Math.max(1,(int)(source.getHeight()*ratio)),java.awt.image.BufferedImage.TYPE_INT_RGB);
    var g=small.createGraphics();try{g.setColor(java.awt.Color.WHITE);g.fillRect(0,0,small.getWidth(),small.getHeight());g.setRenderingHint(java.awt.RenderingHints.KEY_INTERPOLATION,java.awt.RenderingHints.VALUE_INTERPOLATION_BILINEAR);g.drawImage(source,0,0,small.getWidth(),small.getHeight(),null);}finally{g.dispose();}
    var bytes=new ByteArrayOutputStream();ImageIO.write(small,"jpeg",bytes);
    return ResponseEntity.ok().cacheControl(CacheControl.noStore()).contentType(MediaType.IMAGE_JPEG).header("X-Content-Type-Options","nosniff").body(bytes.toByteArray());
   }
  }
  return ResponseEntity.ok().cacheControl(CacheControl.noStore()).contentType(MediaType.parseMediaType(image.contentType())).header("X-Content-Type-Options","nosniff").body(image.data());
 }
}
