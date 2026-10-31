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
 private final Path directory;private final ProductMapper products;private final UserMapper users;
 public ProductImageController(@Value("${app.upload-dir:./uploads}") String path,ProductMapper products,UserMapper users){directory=Path.of(path).toAbsolutePath().normalize();this.products=products;this.users=users;}
 @PostMapping("/api/my/products/{id}/image") public Map<String,String> upload(@PathVariable long id,@RequestParam("file") MultipartFile file,Principal principal) throws IOException {
  long owner=users.find(principal.getName()).id();
  if(products.owned(id,owner)!=1)throw new ResponseStatusException(HttpStatus.NOT_FOUND);
  if(file.isEmpty()||file.getSize()>5*1024*1024)throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"图片应小于5MB");
  java.awt.image.BufferedImage image;
  try(var input=ImageIO.createImageInputStream(file.getInputStream())){
   var readers=ImageIO.getImageReaders(input);if(!readers.hasNext())throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"仅支持JPEG或PNG图片");
   var reader=readers.next();try{reader.setInput(input);String format=reader.getFormatName();if(!(format.equalsIgnoreCase("png")||format.equalsIgnoreCase("jpeg"))||(long)reader.getWidth(0)*reader.getHeight(0)>16000000)throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"图片格式或尺寸无效");image=reader.read(0);}finally{reader.dispose();}
  }catch(javax.imageio.IIOException e){throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"无法读取图片");}
  Files.createDirectories(directory);String name=UUID.randomUUID()+".png";Path target=directory.resolve(name);
  try{ImageIO.write(image,"png",target.toFile());String url="/api/images/"+name;if(products.image(id,owner,url)!=1){Files.deleteIfExists(target);throw new ResponseStatusException(HttpStatus.CONFLICT);}return Map.of("imageUrl",url);}catch(IOException e){Files.deleteIfExists(target);throw e;}
 }
 @GetMapping("/api/images/{name}") public ResponseEntity<Resource> image(@PathVariable String name){
  if(!name.matches("[0-9a-fA-F-]{36}\\.png"))throw new ResponseStatusException(HttpStatus.NOT_FOUND);
  Path file=directory.resolve(name).normalize();if(!file.startsWith(directory)||!Files.isRegularFile(file))throw new ResponseStatusException(HttpStatus.NOT_FOUND);
  return ResponseEntity.ok().contentType(MediaType.IMAGE_PNG).header("X-Content-Type-Options","nosniff").body(new FileSystemResource(file));
 }
}
