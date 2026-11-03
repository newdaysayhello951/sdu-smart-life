package cn.edu.sdu.smartlife;
import java.io.*;
import javax.imageio.ImageIO;
import org.springframework.http.*;
import org.springframework.web.server.ResponseStatusException;
final class ImagePreview {
 static ResponseEntity<byte[]> response(byte[] data,String mime,int width) throws IOException {
  if(width<0||width>1280)throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
  // GIF is kept animated; requesting a preview must not silently destroy frames.
  if(width>0&&!"image/gif".equalsIgnoreCase(mime)){
   var source=ImageIO.read(new ByteArrayInputStream(data));
   if(source!=null){double ratio=Math.min(1d,(double)width/Math.max(source.getWidth(),source.getHeight()));
    var small=new java.awt.image.BufferedImage(Math.max(1,(int)(source.getWidth()*ratio)),Math.max(1,(int)(source.getHeight()*ratio)),java.awt.image.BufferedImage.TYPE_INT_RGB);
    var g=small.createGraphics();try{g.setColor(java.awt.Color.WHITE);g.fillRect(0,0,small.getWidth(),small.getHeight());g.drawImage(source,0,0,small.getWidth(),small.getHeight(),null);}finally{g.dispose();}
    var out=new ByteArrayOutputStream();ImageIO.write(small,"jpeg",out);data=out.toByteArray();mime="image/jpeg";
   }
  }
  return ResponseEntity.ok().cacheControl(CacheControl.noStore()).contentType(MediaType.parseMediaType(mime)).header("X-Content-Type-Options","nosniff").body(data);
 }
}
