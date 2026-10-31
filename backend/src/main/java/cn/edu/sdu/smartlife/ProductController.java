package cn.edu.sdu.smartlife;
import org.springframework.web.bind.annotation.*;
@RestController
@RequestMapping("/api/products")
public class ProductController {
 private final ProductService service;
 public ProductController(ProductService service){this.service=service;}
 @GetMapping public ProductService.Page list(@RequestParam(defaultValue="") String keyword,@RequestParam(defaultValue="1") int page,@RequestParam(defaultValue="12") int size){return service.list(keyword,page,size);}
 @GetMapping("/{id}") public ProductMapper.Product detail(@PathVariable long id){return service.detail(id);}
}
