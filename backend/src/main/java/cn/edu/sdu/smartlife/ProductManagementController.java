package cn.edu.sdu.smartlife;
import java.math.BigDecimal;
import java.security.Principal;
import java.util.List;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
@RestController
@RequestMapping("/api/my/products")
public class ProductManagementController {
 private final ProductMapper products;private final UserMapper users;private final ProductImageController images;
 public ProductManagementController(ProductMapper products,UserMapper users,ProductImageController images){this.products=products;this.users=users;this.images=images;}
 public record Input(@NotBlank @Size(max=120) String title,@NotBlank @Size(max=5000) String description,@NotNull @DecimalMin("0.01") @DecimalMax("99999999.99") @Digits(integer=8,fraction=2) BigDecimal price,@NotBlank @Size(max=120) String location){}
 private long owner(Principal principal){return users.find(principal.getName()).id();}
 @GetMapping public List<ProductMapper.Product> mine(Principal principal){return products.mine(owner(principal));}
 @PostMapping(value="/publish",consumes="multipart/form-data")
 @org.springframework.transaction.annotation.Transactional(rollbackFor=Exception.class)
 @ResponseStatus(HttpStatus.CREATED)
 public java.util.Map<String,Long> publish(@Valid @RequestPart("product") Input input,@RequestPart("file") org.springframework.web.multipart.MultipartFile file,Principal principal) throws java.io.IOException {
  products.create(input.title(),input.description(),input.price(),input.location(),owner(principal));long id=products.lastId();images.upload(id,file,principal);return java.util.Map.of("id",id);
 }
 @PostMapping @ResponseStatus(HttpStatus.CREATED) public void create(@Valid @RequestBody Input input,Principal principal){products.create(input.title(),input.description(),input.price(),input.location(),owner(principal));}
 @PostMapping(value="/{id}/edit-with-image",consumes="multipart/form-data")
 @org.springframework.transaction.annotation.Transactional(rollbackFor=Exception.class)
 @ResponseStatus(HttpStatus.NO_CONTENT)
 public void editWithImage(@PathVariable long id,@Valid @RequestPart("product") Input input,@RequestPart("file") org.springframework.web.multipart.MultipartFile file,Principal principal) throws java.io.IOException {
  if(products.edit(id,owner(principal),input.title(),input.description(),input.price(),input.location())!=1)throw new ResponseStatusException(HttpStatus.NOT_FOUND);
  images.upload(id,file,principal);
 }
 @PutMapping("/{id}") @ResponseStatus(HttpStatus.NO_CONTENT) public void edit(@PathVariable long id,@Valid @RequestBody Input input,Principal principal){if(products.edit(id,owner(principal),input.title(),input.description(),input.price(),input.location())!=1)throw new ResponseStatusException(HttpStatus.NOT_FOUND,"商品不存在或不可操作");}
 @PostMapping("/{id}/withdraw") @ResponseStatus(HttpStatus.NO_CONTENT) public void withdraw(@PathVariable long id,Principal principal){if(products.withdraw(id,owner(principal))!=1)throw new ResponseStatusException(HttpStatus.NOT_FOUND,"鍟嗗搧涓嶅瓨鍦ㄦ垨涓嶅彲鎿嶄綔");}
}
