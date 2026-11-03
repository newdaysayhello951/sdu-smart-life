package cn.edu.sdu.smartlife;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;
import java.io.*;
import javax.imageio.ImageIO;
class AvatarPreviewTest {
 @Test void ownAndOtherAvatarUseBoundedPreview() throws Exception {
  var bitmap=new java.awt.image.BufferedImage(1200,800,java.awt.image.BufferedImage.TYPE_INT_RGB);
  var out=new ByteArrayOutputStream();ImageIO.write(bitmap,"png",out);var bytes=out.toByteArray();
  var profiles=mock(ProfileMapper.class);when(profiles.avatarData(7)).thenReturn(new ProfileMapper.Avatar(bytes));
  var auth=org.springframework.security.authentication.UsernamePasswordAuthenticationToken.authenticated("avatar",null,java.util.List.of());auth.setDetails(7L);
  var own=new ProfileController(profiles).avatar(auth,160);
  var comments=mock(ConversationMapper.class);when(comments.avatar(7)).thenReturn(new ConversationMapper.Avatar(bytes));
  var other=new ConversationController(comments,mock(UserMapper.class),mock(RealtimeHub.class)).avatar(7,160);
  for(var result:java.util.List.of(own,other)){var image=ImageIO.read(new ByteArrayInputStream(result.getBody()));assertEquals(160,image.getWidth());assertTrue(image.getHeight()<=160);}
  assertArrayEquals(bytes,new ProfileController(profiles).avatar(auth,0).getBody());
 }
 @Test void gifStaysAnimatedAndInvalidWidthsFail() throws Exception {
  byte[] gif="GIF89a".getBytes(java.nio.charset.StandardCharsets.US_ASCII);
  assertArrayEquals(gif,ImagePreview.response(gif,"image/gif",640).getBody());
  assertThrows(org.springframework.web.server.ResponseStatusException.class,()->ImagePreview.response(gif,"image/gif",2000));
 }
}
