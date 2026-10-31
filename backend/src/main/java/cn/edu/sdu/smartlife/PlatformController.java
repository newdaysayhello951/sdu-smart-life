package cn.edu.sdu.smartlife;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
@RestController
public class PlatformController {
 @GetMapping("/api/platform")
 public Map<String, String> platform() {
  return Map.of("name", "SDU Smart Life", "status", "migration", "message", "Java 服务已连接");
 }
}
