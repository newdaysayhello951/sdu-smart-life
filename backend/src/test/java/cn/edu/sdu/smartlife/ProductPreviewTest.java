package cn.edu.sdu.smartlife;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;
import java.io.*;
import javax.imageio.ImageIO;
class ProductPreviewTest {
 @Test void previewShrinksPayloadAndPreservesOriginal() throws Exception {
  var source=new java.awt.image.BufferedImage(2400,1600,java.awt.image.BufferedImage.TYPE_INT_RGB);
  var random=new java.util.Random(1);for(int y=0;y<1600;y++)for(int x=0;x<2400;x++)source.setRGB(x,y,random.nextInt());
  var bytes=new ByteArrayOutputStream();ImageIO.write(source,"png",bytes);var original=bytes.toByteArray();
  var images=mock(ProductImageMapper.class);when(images.find(1)).thenReturn(new ProductImageMapper.StoredImage("image/png",original));
  var controller=new ProductImageController(mock(ProductMapper.class),mock(UserMapper.class),images);
  var preview=controller.image(1,960);var decoded=ImageIO.read(new ByteArrayInputStream(preview.getBody()));
  assertEquals(960,decoded.getWidth());assertEquals(640,decoded.getHeight());assertTrue(preview.getBody().length<original.length/4);
  assertArrayEquals(original,controller.image(1,0).getBody());
  assertThrows(org.springframework.web.server.ResponseStatusException.class,()->controller.image(1,2000));
 }
}
