package cn.edu.sdu.smartlife;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;
@Service
public class ProductService {
 private final ProductMapper mapper;
 public ProductService(ProductMapper mapper){this.mapper=mapper;}
 public record Page(List<ProductMapper.Product> items,long total,int page,int size,long snapshot){}
 @org.springframework.transaction.annotation.Transactional(readOnly=true)
 public Page list(String keyword,int page,int size,String kind,long snapshot){
  if(!java.util.List.of("SELL","WANTED","LOST","FOUND").contains(kind))throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
  if(snapshot<0||page<1||page>100000||size<1||size>50||keyword.length()>100)throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"分页或搜索参数无效");
  long boundary=snapshot==0?mapper.latestId():snapshot;
  return new Page(mapper.list(kind,keyword.trim(),size,(page-1)*size,boundary),mapper.count(kind,keyword.trim(),boundary),page,size,boundary);
 }
 public ProductMapper.Product detail(long id){var p=mapper.find(id);if(p==null)throw new ResponseStatusException(HttpStatus.NOT_FOUND,"商品不存在");return p;}
}
